"""Booking endpoints — consultation appointments."""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from django.shortcuts import get_object_or_404

from ..models import Booking
from ..serializers import booking_to_dict


@require_GET
def bookings_root(request):
    """List current user's non-cancelled bookings.

    Booking creation is intentionally handled only by the verified payment flow.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    items = [booking_to_dict(b) for b in request.user.bookings.exclude(status="cancelled")]
    return JsonResponse({"bookings": items})


@csrf_exempt
@require_http_methods(["DELETE"])
def booking_detail(request, booking_id):
    """Cancel a booking (owned by current user)."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.status = "cancelled"
    booking.save(update_fields=["status"])
    return JsonResponse({"ok": True})
