from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create idempotent development users: admin/admin and emre/emre"

    def handle(self, *args, **options):
        User = get_user_model()

        admin, created = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com"})
        if created:
            self.stdout.write("Created admin user")
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("admin")
        admin.save()

        emre, created = User.objects.get_or_create(username="emre", defaults={"email": "emre@example.com"})
        if created:
            self.stdout.write("Created emre user")
        emre.is_staff = False
        emre.is_superuser = False
        emre.set_password("emre")
        emre.save()

        self.stdout.write(self.style.SUCCESS("Dev users ensured: admin/admin, emre/emre"))


