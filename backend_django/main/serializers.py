"""Helpers to serialize models into JSON-safe dicts."""


def user_to_dict(user, request=None):
    """Serialize a Django User + related profile to a dict."""
    profile = getattr(user, "profile", None)
    avatar_url = None
    if profile and profile.avatar:
        avatar_url = profile.avatar.url
        if request is not None:
            avatar_url = request.build_absolute_uri(avatar_url)
    return {
        "id": user.id,
        "name": (user.get_full_name() or user.username).strip(),
        "email": user.email,
        "phone": profile.phone if profile else "",
        "country": profile.country if profile else "",
        "avatar": avatar_url,
        "joined": profile.joined.strftime("%b %Y") if profile else "",
    }


def booking_to_dict(booking):
    try:
        payment = booking.payment
    except Exception:
        payment = None
    return {
        "id": booking.id,
        "consultantId": booking.consultant_id,
        "consultantName": booking.consultant_name,
        "date": booking.date,
        "time": booking.time,
        "name": booking.name,
        "email": booking.email,
        "message": booking.message,
        "status": booking.status,
        "createdAt": booking.created_at.isoformat(),
        "invoiceUrl": f"/api/payments/{payment.id}/invoice" if payment and payment.status == "paid" else None,
    }


def shortlist_to_list(user):
    return list(user.shortlist.values_list("university_id", flat=True))


def compare_to_list(user):
    return list(user.compare.values_list("university_id", flat=True))
