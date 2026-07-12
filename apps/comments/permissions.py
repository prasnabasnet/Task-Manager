from rest_framework import permissions

from apps.comments.models import Comment
from apps.organization.models import Organization
from apps.projects.models import Project
from apps.tasks.models import Task


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsProjectMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False

        if getattr(request.user, "role", None) == "ADMIN":
            return True

        if isinstance(obj, Organization):
            return (
                obj.owner == request.user
                or obj.memberships.filter(user=request.user).exists()
            )

        if isinstance(obj, Project):
            project = obj
        elif isinstance(obj, Task):
            project = obj.project
        elif isinstance(obj, Comment):
            target = obj.commentable_object
            if isinstance(target, Organization):
                return (
                    target.owner == request.user
                    or target.memberships.filter(user=request.user).exists()
                )
            elif isinstance(target, Project):
                project = target
            elif isinstance(target, Task):
                project = target.project
            else:
                return False
        else:
            return False

        return (
            project.owner == request.user
            or project.members.filter(id=request.user.id).exists()
        )


class IsCommentAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.role == "ADMIN":
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user
