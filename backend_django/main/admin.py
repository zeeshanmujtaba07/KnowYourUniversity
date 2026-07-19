"""Django admin registrations — with rich pagination, filters and search."""
from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, ShortlistItem, CompareItem, Booking, Payment


# ---------------- User Profile ----------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "phone", "country", "avatar_thumb", "joined")
    list_filter = ("country", "joined")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "phone", "country")
    ordering = ("-joined",)
    list_per_page = 25
    date_hierarchy = "joined"
    readonly_fields = ("joined", "avatar_preview")
    fieldsets = (
        ("User Link", {"fields": ("user",)}),
        ("Contact & Location", {"fields": ("phone", "country")}),
        ("Profile Picture", {"fields": ("avatar", "avatar_preview")}),
        ("Meta", {"fields": ("joined",)}),
    )

    @admin.display(description="Email", ordering="user__email")
    def email(self, obj):
        return obj.user.email

    @admin.display(description="Avatar")
    def avatar_thumb(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="height:32px;width:32px;border-radius:50%;object-fit:cover"/>', obj.avatar.url)
        return "—"

    @admin.display(description="Preview")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="max-height:140px;border-radius:12px"/>', obj.avatar.url)
        return "No avatar uploaded"


# ---------------- Shortlist ----------------
@admin.register(ShortlistItem)
class ShortlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "user_email", "university_id", "added_at")
    list_filter = ("added_at", "university_id")
    search_fields = ("user__username", "user__email", "university_id")
    ordering = ("-added_at",)
    list_per_page = 50
    date_hierarchy = "added_at"
    autocomplete_fields = ("user",)

    @admin.display(description="Email", ordering="user__email")
    def user_email(self, obj):
        return obj.user.email


# ---------------- Compare ----------------
@admin.register(CompareItem)
class CompareItemAdmin(admin.ModelAdmin):
    list_display = ("user", "user_email", "university_id", "added_at")
    list_filter = ("added_at", "university_id")
    search_fields = ("user__username", "user__email", "university_id")
    ordering = ("-added_at",)
    list_per_page = 50
    date_hierarchy = "added_at"
    autocomplete_fields = ("user",)

    @admin.display(description="Email", ordering="user__email")
    def user_email(self, obj):
        return obj.user.email


# ---------------- Bookings ----------------
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "user_email", "consultant_name", "consultant_id",
                    "date", "time", "status_badge", "created_at")
    list_display_links = ("id", "user")
    list_filter = ("status", "consultant_id", "created_at")
    list_editable = ()
    search_fields = ("user__username", "user__email", "consultant_name",
                     "consultant_id", "name", "email", "message")
    ordering = ("-created_at",)
    list_per_page = 25
    date_hierarchy = "created_at"
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Who", {"fields": ("user", "name", "email")}),
        ("Consultant", {"fields": ("consultant_id", "consultant_name")}),
        ("When", {"fields": ("date", "time")}),
        ("Details", {"fields": ("message", "status", "created_at")}),
    )
    actions = ("mark_confirmed", "mark_cancelled", "mark_completed")

    @admin.display(description="Email", ordering="user__email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        colors = {"confirmed": "#10B981", "cancelled": "#EF4444", "completed": "#6366F1"}
        color = colors.get(obj.status, "#6B7280")
        return format_html(
            '<span style="background:{}22;color:{};padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.05em">{}</span>',
            color, color, obj.status
        )

    @admin.action(description="Mark selected as CONFIRMED")
    def mark_confirmed(self, request, queryset):
        n = queryset.update(status="confirmed")
        self.message_user(request, f"{n} booking(s) marked as confirmed.")

    @admin.action(description="Mark selected as CANCELLED")
    def mark_cancelled(self, request, queryset):
        n = queryset.update(status="cancelled")
        self.message_user(request, f"{n} booking(s) cancelled.")

    @admin.action(description="Mark selected as COMPLETED")
    def mark_completed(self, request, queryset):
        n = queryset.update(status="completed")
        self.message_user(request, f"{n} booking(s) marked as completed.")


# ---------------- Payments ----------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "razorpay_order_id", "razorpay_payment_id", "amount_display", "status", "paid_at")
    list_filter = ("status", "currency", "created_at", "paid_at")
    search_fields = ("user__username", "user__email", "razorpay_order_id", "razorpay_payment_id")
    ordering = ("-created_at",)
    readonly_fields = ("user", "booking", "razorpay_order_id", "razorpay_payment_id", "amount_paise", "currency", "status", "booking_data", "created_at", "paid_at")

    @admin.display(description="Amount")
    def amount_display(self, obj):
        return f"₹{obj.amount_paise / 100:.2f} {obj.currency}"


# ---------------- User admin patch (enable autocomplete) ----------------
# The default UserAdmin already has search_fields on username/email/first_name/last_name,
# which is what autocomplete_fields=("user",) above needs. No further changes required.
