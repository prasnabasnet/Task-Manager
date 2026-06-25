from rest_framework import permissions


class IsAdminOrPM(permissions.BasePermission):
    """Allow access only to Admin or Project Manager roles."""

    def has_permission(self, request, view):
        return request.user.role in ('ADMIN', 'PM')


class IsProjectOwnerOrAdmin(permissions.BasePermission):
    """Allow object-level access only to the project owner or admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        return obj.owner == request.user


class IsProjectMemberOrAdmin(permissions.BasePermission):
    """Allow access only to project members or admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        return obj.members.filter(id=request.user.id).exists() or obj.owner == request.user