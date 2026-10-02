from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.authentication.models import User
from django.db import connection


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

        # 2. Seed Legacy/Accounts Admin table if present in DB
        admin_status = "Skipped"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts_admin';")
                if cursor.fetchone():
                    cursor.execute("SELECT id FROM accounts_admin WHERE email = %s;", [email])
                    row = cursor.fetchone()
                    hashed = make_password(password)
                    if row:
                        cursor.execute("UPDATE accounts_admin SET password = %s, name = %s WHERE id = %s;", [hashed, 'Pashupati Admin', row[0]])
                        admin_status = "Updated"
                    else:
                        cursor.execute(
                            "INSERT INTO accounts_admin (name, email, password, phone, address, note) VALUES (%s, %s, %s, %s, %s, %s);",
                            ['Pashupati Admin', email, hashed, '+977-9800000000', 'Admin Headquarters', 'Super Administrator']
                        )
                        admin_status = "Created"
        except Exception as e:
            admin_status = f"Error: {e}"

        user_status = "Created" if user_created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded admin credentials:\n"
                f"  - Email: {email}\n"
                f"  - Password: {password}\n"
                f"  - Auth User: {user_status}\n"
                f"  - Accounts Admin: {admin_status}"
            )
        )
