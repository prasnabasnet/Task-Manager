from rest_framework.permissions import BasePermission


class IsAdminOrOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", "") in ("SUPERADMIN", "ORG_ADMIN") or request.user.is_superuser:
            return obj.owner == request.user or request.user.role == "SUPERADMIN" or request.user.is_superuser
        return False


class CanCreateOrganization(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == "SUPERADMIN" or request.user.is_superuser)
        )


