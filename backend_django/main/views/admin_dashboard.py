"""Custom staff-only admin dashboard view — a landing page for /admin."""
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

from ..models import UserProfile, ShortlistItem, CompareItem, Booking


@staff_member_required
def admin_dashboard(request):
    """A simple, clean overview dashboard shown at /dashboard/ (staff only)."""
    now = timezone.now()
    last_7 = now - timedelta(days=7)

    total_users = User.objects.count()
    total_profiles = UserProfile.objects.count()
    total_shortlist = ShortlistItem.objects.count()
    total_compare = CompareItem.objects.count()
    total_bookings = Booking.objects.count()

    new_users_7d = User.objects.filter(date_joined__gte=last_7).count()
    new_bookings_7d = Booking.objects.filter(created_at__gte=last_7).count()

    confirmed_bookings = Booking.objects.filter(status="confirmed").count()
    cancelled_bookings = Booking.objects.filter(status="cancelled").count()
    completed_bookings = Booking.objects.filter(status="completed").count()

    recent_users = User.objects.order_by("-date_joined")[:6]
    recent_bookings = Booking.objects.select_related("user").order_by("-created_at")[:6]

    top_universities = (
        ShortlistItem.objects
        .values("university_id")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )
    top_consultants = (
        Booking.objects
        .values("consultant_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    context = {
        "total_users": total_users,
        "total_profiles": total_profiles,
        "total_shortlist": total_shortlist,
        "total_compare": total_compare,
        "total_bookings": total_bookings,
        "new_users_7d": new_users_7d,
        "new_bookings_7d": new_bookings_7d,
        "confirmed_bookings": confirmed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "completed_bookings": completed_bookings,
        "recent_users": recent_users,
        "recent_bookings": recent_bookings,
        "top_universities": top_universities,
        "top_consultants": top_consultants,
    }
    return render(request, "main/dashboard.html", context)
