"""URL routes for the main app — all under /api/."""
from django.urls import path
from .views import auth_views, profile_views, shortlist_views, compare_views, booking_views, payment_views

urlpatterns = [
    # Auth
    path("auth/signup", auth_views.signup, name="signup"),
    path("auth/login", auth_views.login_view, name="login"),
    path("auth/logout", auth_views.logout_view, name="logout"),
    path("auth/me", auth_views.me, name="me"),
    path("auth/change-password", auth_views.change_password, name="change_password"),

    # Profile
    path("profile", profile_views.profile_detail, name="profile"),
    path("profile/avatar", profile_views.upload_avatar, name="profile_avatar"),

    # Shortlist
    path("shortlist", shortlist_views.list_shortlist, name="shortlist_list"),
    path("shortlist/<str:university_id>", shortlist_views.toggle_shortlist, name="shortlist_toggle"),

    # Compare
    path("compare", compare_views.list_compare, name="compare_list"),
    path("compare/<str:university_id>", compare_views.toggle_compare, name="compare_toggle"),

    # Bookings
    path("bookings", booking_views.bookings_root, name="bookings_root"),
    path("bookings/<int:booking_id>", booking_views.booking_detail, name="booking_detail"),

    # Payments
    path("payments/create-order", payment_views.create_order, name="payment_create_order"),
    path("payments/verify", payment_views.verify_payment, name="payment_verify"),
    path("payments/webhook", payment_views.razorpay_webhook, name="payment_webhook"),
    path("payments/<int:payment_id>", payment_views.payment_detail, name="payment_detail"),
    path("payments/<int:payment_id>/invoice", payment_views.invoice, name="payment_invoice"),
]
