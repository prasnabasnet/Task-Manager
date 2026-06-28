from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.tasks.models import Task
from apps.projects.models import Project
from .models import Comment
from .serializers import CommentSerializer


class IsProjectMemberMixin:
    """Mixin to check if user is admin, project owner, or project member."""
    def check_project_membership(self, project, user):
        if user.role == 'ADMIN':
            return True
        if project.owner == user:
            return True
        if project.members.filter(id=user.id).exists():
            return True
        raise PermissionDenied("You must be a member of the project to perform this action.")


class TaskCommentListCreateView(IsProjectMemberMixin, generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_task_and_project(self):
        project = get_object_or_404(Project, pk=self.kwargs.get('pid'))
        task = get_object_or_404(Task, pk=self.kwargs.get('tid'), project=project)
        return project, task

    def get_queryset(self):
        project, task = self.get_task_and_project()
        self.check_project_membership(project, self.request.user)
        # Return top-level comments only (parent is null) as replies are nested
        return Comment.objects.filter(task=task, parent__isnull=True)

    def perform_create(self, serializer):
        project, task = self.get_task_and_project()
        self.check_project_membership(project, self.request.user)
        
        # If parent is provided in request data, validate that it belongs to the same task
        parent_id = self.request.data.get('parent')
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, pk=parent_id, task=task)

        serializer.save(task=task, parent=parent, author=self.request.user)


class CommentDetailView(IsProjectMemberMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        comment = super().get_object()
        # Enforce project membership for read access
        self.check_project_membership(comment.task.project, self.request.user)
        
        # Enforce author or admin for update/delete actions
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if self.request.user.role != 'ADMIN' and comment.author != self.request.user:
                raise PermissionDenied("Only the author or an admin can edit/delete this comment.")
        
        return comment

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        self.perform_destroy(comment)
        return Response(status=status.HTTP_204_NO_CONTENT)
