from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.authentication.models import User
from accounts.models import Admin


class Command(BaseCommand):
    help = "Seed superuser/admin 'pashupati@python.py' with password 'Forgot911!'"

    def handle(self, *args, **options):
        email = 'pashupati@python.py'
        username = 'pashupati'
        password = 'Forgot911!'

        # 1. Seed Custom Auth User model
        user, user_created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': 'Pashupati',
                'last_name': 'Admin',
                'user_type': 'admin',
                'access_type': 'full_access',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.user_type = 'admin'
        user.is_active = True
        user.save()

        # 2. Seed Legacy/Accounts Admin model for Django template login
        admin, admin_created = Admin.objects.get_or_create(
            email=email,
            defaults={
                'name': 'Pashupati Admin',
                'phone': '+977-9800000000',
                'address': 'Admin Headquarters',
                'note': 'Super Administrator',
            }
        )
        admin.name = 'Pashupati Admin'
        admin.password = make_password(password)
        admin.save()

        user_status = "Created" if user_created else "Updated"
        admin_status = "Created" if admin_created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded admin credentials:\n"
                f"  - Email: {email}\n"
                f"  - Password: {password}\n"
                f"  - Auth User: {user_status}\n"
                f"  - Accounts Admin: {admin_status}"
            )
        )
