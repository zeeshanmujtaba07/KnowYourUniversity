"""Database models for the main app."""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended profile for each Django User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=32, blank=True, default="")
    country = models.CharField(max_length=64, blank=True, default="")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} profile"


class ShortlistItem(models.Model):
    """A university a user has bookmarked."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shortlist")
    university_id = models.CharField(max_length=64)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "university_id")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} → {self.university_id}"


class CompareItem(models.Model):
    """A university a user has added to the compare list (max 3)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="compare")
    university_id = models.CharField(max_length=64)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "university_id")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} ↔ {self.university_id}"


class Booking(models.Model):
    """A consultation booking with a consultant."""
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    consultant_id = models.CharField(max_length=64)
    consultant_name = models.CharField(max_length=128)
    date = models.CharField(max_length=64)   # formatted date string
    time = models.CharField(max_length=32)   # e.g., "09:00 AM"
    name = models.CharField(max_length=128, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    message = models.TextField(blank=True, default="")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.consultant_name} @ {self.date} {self.time}"


class Payment(models.Model):
    """A Razorpay order and its verified payment outcome.

    No card, UPI, or bank details are stored here; Razorpay handles them.
    """
    STATUS_CHOICES = [
        ("created", "Created"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    booking = models.OneToOneField(
        Booking, on_delete=models.SET_NULL, related_name="payment", null=True, blank=True
    )
    razorpay_order_id = models.CharField(max_length=64, unique=True)
    razorpay_payment_id = models.CharField(max_length=64, unique=True, null=True, blank=True)
    amount_paise = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="created")
    # A server-side snapshot prevents the browser from changing booking details
    # between checkout creation and signature verification.
    booking_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.razorpay_order_id} ({self.status})"
