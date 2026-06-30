from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.tasks.models import Task
from apps.projects.models import Project
from apps.comments.models import Comment
from apps.comments.serializers import CommentSerializer
from .permissions import IsProjectMember, IsCommentAuthorOrAdmin, IsAdmin


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated, IsProjectMember]

        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes.append(IsCommentAuthorOrAdmin)

        return [permission() for permission in permission_classes]

    def _get_project_and_task(self):
        project = get_object_or_404(Project, pk=self.kwargs.get('pid'))
        task = get_object_or_404(Task, pk=self.kwargs.get('tid'), project=project)
        return project, task

    def get_queryset(self):
        project, task = self._get_project_and_task()
        
        # Explicitly trigger object permission check for the project structure on list/create routes
        # because DRF doesn't call `has_object_permission` automatically for lists.
        for permission in self.get_permissions():
            if not permission.has_object_permission(self.request, self, task):
                self.permission_denied(self.request)

        # Return top-level comments only (parent is null) as replies are nested
        return Comment.objects.filter(task=task, parent__isnull=True)

    def perform_create(self, serializer):
        project, task = self._get_project_and_task()
        
        # If a parent ID is provided, validate it belongs to the same task
        parent_id = self.request.data.get('parent')
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, pk=parent_id, task=task)

        serializer.save(task=task, parent=parent, author=self.request.user)