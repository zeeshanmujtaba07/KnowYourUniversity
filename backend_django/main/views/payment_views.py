"""Razorpay payment endpoints for paid consultation bookings."""
import hashlib
import hmac
import json
import uuid
from io import BytesIO
from xml.sax.saxutils import escape

import razorpay
from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..forms import BookingForm
from ..models import Booking, Payment
from ..serializers import booking_to_dict


def _client():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return None
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def _json(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _booking_snapshot(cleaned_data):
    return {
        "consultant_id": cleaned_data["consultant_id"],
        "consultant_name": cleaned_data["consultant_name"],
        "date": cleaned_data["date"],
        "time": cleaned_data["time"],
        "name": cleaned_data.get("name") or "",
        "email": cleaned_data.get("email") or "",
        "message": cleaned_data.get("message") or "",
    }


def _receipt_pdf(payment, booking):
    """Create a one-page PDF payment receipt using a compact business layout."""
    output = BytesIO()
    document = SimpleDocTemplate(
        output, pagesize=LETTER, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    brand = ParagraphStyle(
        "ReceiptBrand", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=22,
        leading=27, textColor=colors.HexColor("#D79600"), spaceAfter=18,
    )
    subtitle = ParagraphStyle(
        "ReceiptSubtitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10,
        leading=13, textColor=colors.HexColor("#4B5563"), spaceAfter=20,
    )
    status = ParagraphStyle(
        "ReceiptStatus", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=13,
        leading=16, textColor=colors.HexColor("#16803B"), spaceAfter=14,
    )
    label = ParagraphStyle(
        "ReceiptLabel", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11,
        leading=14, textColor=colors.HexColor("#1F3A5F"), alignment=TA_LEFT,
    )
    value = ParagraphStyle(
        "ReceiptValue", parent=styles["Normal"], fontName="Helvetica", fontSize=11,
        leading=14, textColor=colors.HexColor("#111827"), alignment=TA_LEFT,
    )
    note = ParagraphStyle(
        "ReceiptNote", parent=styles["Normal"], fontName="Helvetica", fontSize=9,
        leading=12, textColor=colors.HexColor("#4B5563"), spaceBefore=16,
    )
    rows = [
        ("Receipt number", f"KYU-{payment.id:06d}"),
        ("Paid on", payment.paid_at.strftime("%d %b %Y, %I:%M %p")),
        ("Consultant", booking.consultant_name),
        ("Session", f"{booking.date} at {booking.time}"),
        ("Customer", f"{booking.name} ({booking.email})"),
        ("Amount paid", f"INR {payment.amount_paise / 100:.2f}"),
        ("Payment reference", payment.razorpay_payment_id or ""),
    ]
    table = Table(
        [[Paragraph(escape(key), label), Paragraph(escape(str(val)), value)] for key, val in rows],
        colWidths=[1.75 * inch, 4.35 * inch],
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    document.build([
        Paragraph("knowYourUniversity", brand),
        Paragraph("CONSULTATION PAYMENT RECEIPT", subtitle),
        Paragraph("PAID", status),
        table,
        Spacer(1, 2),
        Paragraph("This receipt confirms payment for the consultation shown above.", note),
    ])
    return output.getvalue()


@transaction.atomic
def _complete_payment(payment, razorpay_payment_id):
    """Create exactly one booking after a trusted payment confirmation."""
    payment = Payment.objects.select_for_update().get(pk=payment.pk)
    if payment.status == "paid":
        return payment, False
    if payment.status != "created":
        raise ValueError("This payment is no longer available for completion.")

    data = payment.booking_data
    booking = Booking.objects.create(user=payment.user, **data)
    payment.booking = booking
    payment.razorpay_payment_id = razorpay_payment_id
    payment.status = "paid"
    payment.paid_at = timezone.now()
    payment.save(update_fields=["booking", "razorpay_payment_id", "status", "paid_at"])
    return payment, True


@csrf_exempt
@require_POST
def create_order(request):
    """Validate booking details and create a Razorpay order on the server."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Please log in before making a payment."}, status=401)
    client = _client()
    if client is None:
        return JsonResponse({"error": "Payments are not configured on this server."}, status=503)

    data = _json(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    form = BookingForm(data)
    if not form.is_valid():
        return JsonResponse({"error": "Validation failed", "details": form.errors}, status=400)

    try:
        order = client.order.create({
            "amount": settings.CONSULTATION_FEE_PAISE,
            "currency": "INR",
            "receipt": f"kyu_{uuid.uuid4().hex[:28]}",
            "notes": {"user_id": str(request.user.id), "service": "consultation"},
        })
        payment = Payment.objects.create(
            user=request.user,
            razorpay_order_id=order["id"],
            amount_paise=settings.CONSULTATION_FEE_PAISE,
            booking_data=_booking_snapshot(form.cleaned_data),
        )
    except Exception:
        return JsonResponse({"error": "Unable to start payment. Please try again."}, status=502)

    return JsonResponse({
        "paymentId": payment.id,
        "orderId": payment.razorpay_order_id,
        "amount": payment.amount_paise,
        "currency": payment.currency,
        # Razorpay Key ID is public; the secret never leaves the server.
        "keyId": settings.RAZORPAY_KEY_ID,
    }, status=201)


@csrf_exempt
@require_POST
def verify_payment(request):
    """Verify Razorpay's checkout signature and only then create the booking."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    client = _client()
    if client is None:
        return JsonResponse({"error": "Payments are not configured on this server."}, status=503)

    data = _json(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    try:
        payment = Payment.objects.get(pk=int(data.get("paymentId")), user=request.user)
    except (Payment.DoesNotExist, TypeError, ValueError):
        return JsonResponse({"error": "Payment session not found."}, status=404)
    if payment.status == "paid":
        return JsonResponse({"booking": booking_to_dict(payment.booking), "paymentId": payment.id})
    if payment.status != "created":
        return JsonResponse({"error": "This payment cannot be completed."}, status=400)

    payment_id = data.get("razorpay_payment_id", "")
    order_id = data.get("razorpay_order_id", "")
    signature = data.get("razorpay_signature", "")
    if not all([payment_id, order_id, signature]) or order_id != payment.razorpay_order_id:
        return JsonResponse({"error": "Invalid payment confirmation."}, status=400)
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": payment.razorpay_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })
        gateway_payment = client.payment.fetch(payment_id)
    except Exception:
        return JsonResponse({"error": "Payment verification failed. No booking was created."}, status=400)

    if gateway_payment.get("order_id") != payment.razorpay_order_id or gateway_payment.get("status") != "captured":
        return JsonResponse({"error": "Payment is not captured yet. Please wait a moment and check your dashboard."}, status=409)
    if gateway_payment.get("amount") != payment.amount_paise or gateway_payment.get("currency") != payment.currency:
        return JsonResponse({"error": "Payment amount could not be verified."}, status=400)
    try:
        payment, _ = _complete_payment(payment, payment_id)
    except (ValueError, IntegrityError):
        return JsonResponse({"error": "Payment could not be completed safely."}, status=409)
    return JsonResponse({
        "booking": booking_to_dict(payment.booking),
        "paymentId": payment.id,
        "invoiceUrl": f"/api/payments/{payment.id}/invoice",
    })


@csrf_exempt
@require_POST
def razorpay_webhook(request):
    """Reconcile payment outcomes even if the browser closes after checkout."""
    if not settings.RAZORPAY_WEBHOOK_SECRET:
        return JsonResponse({"error": "Webhook is not configured."}, status=503)
    signature = request.headers.get("X-Razorpay-Signature", "")
    expected = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(), request.body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return JsonResponse({"error": "Invalid webhook signature."}, status=400)
    data = _json(request)
    if data is None:
        return JsonResponse({"error": "Invalid webhook body."}, status=400)

    event = data.get("event")
    entity = data.get("payload", {}).get("payment", {}).get("entity", {})
    order_id = entity.get("order_id")
    if not order_id:
        return JsonResponse({"ok": True})
    try:
        payment = Payment.objects.get(razorpay_order_id=order_id)
    except Payment.DoesNotExist:
        return JsonResponse({"ok": True})

    if event == "payment.captured":
        if entity.get("amount") == payment.amount_paise and entity.get("currency") == payment.currency:
            try:
                _complete_payment(payment, entity.get("id", ""))
            except (ValueError, IntegrityError):
                pass
    elif event == "payment.failed" and payment.status == "created":
        payment.status = "failed"
        payment.save(update_fields=["status"])
    return JsonResponse({"ok": True})


@require_GET
def payment_detail(request, payment_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    try:
        payment = Payment.objects.get(pk=payment_id, user=request.user)
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Payment not found"}, status=404)
    return JsonResponse({
        "id": payment.id, "status": payment.status, "amount": payment.amount_paise,
        "currency": payment.currency, "invoiceUrl": f"/api/payments/{payment.id}/invoice" if payment.status == "paid" else None,
    })


@require_GET
def invoice(request, payment_id):
    """Download a PDF receipt for a verified consultation payment."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    try:
        payment = Payment.objects.select_related("booking").get(pk=payment_id, user=request.user, status="paid")
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Paid invoice not found"}, status=404)
    booking = payment.booking
    response = HttpResponse(
        _receipt_pdf(payment, booking),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = f'attachment; filename="KYU-receipt-{payment.id}.pdf"'
    return response
