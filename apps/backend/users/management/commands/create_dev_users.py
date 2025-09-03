import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create idempotent development users with demo data"

    def handle(self, *args, **options):
        User = get_user_model()
        avatar_base = os.getenv("DEMO_AVATAR_BASE", "https://i.pravatar.cc")

        # Admin user
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "full_name": "Admin User",
                "avatar": f"{avatar_base.rstrip('/')}/150?u=admin",
                "about": "System Administrator",
            },
        )
        if created:
            self.stdout.write("Created admin user")
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("admin")
        admin.save()

        # Emre user
        emre, created = User.objects.get_or_create(
            username="emre",
            defaults={
                "email": "emre@example.com",
                "full_name": "Emre Almaoğlu",
                "avatar": f"{avatar_base.rstrip('/')}/150?u=emre",
                "about": "Full Stack Developer",
            },
        )
        if created:
            self.stdout.write("Created emre user")
        emre.is_staff = False
        emre.is_superuser = False
        emre.set_password("emre")
        emre.save()

        # Demo user Ayşe
        ayse, created = User.objects.get_or_create(
            username="ayse",
            defaults={
                "email": "ayse@demo.trailium.com",
                "full_name": "Ayşe Kara",
                "avatar": f"{avatar_base.rstrip('/')}/150?u=ayse",
                "about": "Marketing Specialist at N2Mobil",
                "phone": "+90 533 245 7812",
                "gender": "F",
            },
        )
        if created:
            self.stdout.write("Created Ayşe demo user")
        ayse.set_password("ayse123")
        ayse.save()

        # Demo user Mehmet
        mehmet, created = User.objects.get_or_create(
            username="mehmet",
            defaults={
                "email": "mehmet@demo.trailium.com",
                "full_name": "Mehmet Yılmaz",
                "avatar": f"{avatar_base.rstrip('/')}/150?u=mehmet",
                "about": "Software Engineer",
                "phone": "+90 555 123 4567",
                "gender": "M",
            },
        )
        if created:
            self.stdout.write("Created Mehmet demo user")
        mehmet.set_password("mehmet123")
        mehmet.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Dev users ensured: admin/admin, emre/emre, ayse/ayse123, mehmet/mehmet123"
            )
        )
