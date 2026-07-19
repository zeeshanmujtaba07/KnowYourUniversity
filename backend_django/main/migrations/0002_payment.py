# Generated manually for the Razorpay payment integration.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("main", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("razorpay_order_id", models.CharField(max_length=64, unique=True)),
                ("razorpay_payment_id", models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ("amount_paise", models.PositiveIntegerField()),
                ("currency", models.CharField(default="INR", max_length=3)),
                ("status", models.CharField(choices=[("created", "Created"), ("paid", "Paid"), ("failed", "Failed")], default="created", max_length=16)),
                ("booking_data", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("booking", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payment", to="main.booking")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
