from rest_framework.permissions import BasePermission


class IsAdminOrPM(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ('ADMIN', 'PM')


class IsProjectOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        return obj.owner == request.user


class IsProjectMemberOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        return obj.members.filter(id=request.user.id).exists() or obj.owner == request.user