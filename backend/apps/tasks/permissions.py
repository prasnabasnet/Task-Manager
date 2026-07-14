from rest_framework.permissions import BasePermission


class IsProjectMemberForTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "is_admin", False):
            return True
        project = obj.project
        return (
            project.owner == request.user
            or project.members.filter(id=request.user.id).exists()
        )


class CanModifyTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "is_admin", False):
            return True
        if obj.project.owner == request.user:
            return True
        if obj.created_by_id == request.user.id:
            return True
        if obj.assignee_id == request.user.id:
            return True
        return False


class CanDeleteTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "is_admin", False):
            return True
        if obj.created_by_id == request.user.id:
            return True
        return False
