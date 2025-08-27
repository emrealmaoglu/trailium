from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    """
    Allow access only to superusers.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_superuser
        )


class IsAdminUser(permissions.BasePermission):
    """
    Allow access only to admin users (staff + superuser).
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Allow read access to all users, but write access only to admin users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Allow read access to all users, but write access only to superusers.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user and request.user.is_authenticated and request.user.is_superuser
        )
