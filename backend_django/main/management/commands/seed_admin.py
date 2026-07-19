"""Create the default admin superuser (admin / admin123) if it does not exist."""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed a default admin superuser (username=admin, password=admin123)"

    def handle(self, *args, **options):
        username = "admin"
        email = "admin@knowyouruniversity.local"
        password = "admin123"

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f"Admin user '{username}' already exists — skipping."
            ))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(
            f"Superuser created ✓  username: {username}   password: {password}"
        ))
        self.stdout.write(self.style.SUCCESS(
            "Open the admin dashboard at:  http://localhost:8000/dashboard/"
        ))
