from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Enterprise Custom User Model matching Fack News Detection specification.
    """
    first_name = models.CharField(max_length=150, blank=True, default='')
    middle_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    mobile = models.CharField(max_length=50, blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    address = models.TextField(blank=True, default='')
    user_type = models.CharField(max_length=50, default='admin', db_index=True)
    access_type = models.CharField(max_length=100, blank=True, null=True)

    is_mfa_enabled = models.BooleanField(default=False)
    is_email_authentication_enabled = models.BooleanField(default=False)
    mfa_secret_code = models.CharField(max_length=255, blank=True, null=True)
    mfa_authentication_image = models.TextField(blank=True, null=True, help_text="QR or authentication image path/data")

    is_active = models.BooleanField(default=True)
    last_logged_in = models.DateTimeField(null=True, blank=True)

    # Standard Django auth requirement fields
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        assembled = " ".join(p for p in parts if p).strip()
        return assembled or self.username or self.email

    def __str__(self):
        return f"{self.email} ({self.full_name})"
