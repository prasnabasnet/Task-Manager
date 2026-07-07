from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsSelfOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'ADMIN' or obj == request.user


class IsAdminOrOrgOwner(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_admin:
            return True
        
        oid = view.kwargs.get('oid')
        if oid:
            from apps.organization.models import Organization
            try:
                org = Organization.objects.get(pk=oid)
                return org.owner == request.user
            except Organization.DoesNotExist:
                return False
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj.organization.owner == request.user