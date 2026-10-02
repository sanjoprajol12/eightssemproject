from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """
    Allows access only to authenticated users who have administrative privileges:
    - user.user_type == 'admin', OR
    - user.is_staff == True, OR
    - user.is_superuser == True
    """
    message = "Administrative credentials required for this CMS operation."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        user_type = getattr(request.user, 'user_type', '')
        return bool(
            request.user.is_superuser
            or request.user.is_staff
            or str(user_type).lower() == 'admin'
        )
