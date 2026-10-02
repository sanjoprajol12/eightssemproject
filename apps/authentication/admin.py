from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'username',
        'full_name',
        'mobile',
        'user_type',
        'is_active',
        'is_mfa_enabled',
        'last_logged_in',
        'is_staff',
    )
    list_filter = (
        'user_type',
        'is_active',
        'is_mfa_enabled',
        'is_email_authentication_enabled',
        'is_staff',
        'is_superuser',
    )
    search_fields = (
        'email',
        'username',
        'first_name',
        'middle_name',
        'last_name',
        'mobile',
        'phone',
    )
    ordering = ('-date_joined',)
    readonly_fields = ('last_logged_in', 'date_joined', 'full_name')

    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Information', {
            'fields': (
                'first_name',
                'middle_name',
                'last_name',
                'full_name',
                'mobile',
                'phone',
                'address',
            )
        }),
        ('Role & Access Configuration', {
            'fields': (
                'user_type',
                'access_type',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Security & Multi-Factor Auth (MFA)', {
            'fields': (
                'is_mfa_enabled',
                'is_email_authentication_enabled',
                'mfa_secret_code',
                'mfa_authentication_image',
            )
        }),
        ('Activity Timestamps', {
            'fields': ('last_logged_in', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'password',
                'first_name',
                'middle_name',
                'last_name',
                'mobile',
                'phone',
                'address',
                'user_type',
                'access_type',
                'is_active',
                'is_staff',
            ),
        }),
    )
