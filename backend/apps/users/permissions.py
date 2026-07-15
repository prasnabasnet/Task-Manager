from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == "ADMIN" or request.user.is_superuser)
        )


class IsSelfOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return request.user.role == "ADMIN" or obj == request.user


class IsAdminOrOrgOwner(BasePermission):
    """
    Permission to check if the user is a site Admin OR the owner
    of the organization associated with the request.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == "ADMIN" or request.user.is_superuser:
            return True

        oid = view.kwargs.get("oid")
        if oid:
            from apps.organization.models import Organization

            try:
                org = Organization.objects.get(pk=oid)
                return org.owner == request.user
            except Organization.DoesNotExist:
                return False
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMIN" or request.user.is_superuser:
            return True
        # Assumes the object has an 'organization' attribute
        return (
            getattr(obj, "organization", None)
            and obj.organization.owner == request.user
        )
