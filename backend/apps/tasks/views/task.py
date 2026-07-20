from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.tasks.filters import TaskFilter
from apps.tasks.models.task import Task
from apps.tasks.permissions import CanDeleteTask, CanModifyTask, IsProjectMemberForTask
from apps.tasks.serializers.task import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter, SearchFilter]
    filterset_class = TaskFilter

    search_fields = ["title", "description"]
    ordering_fields = ["due_date", "priority", "created_at"]
    ordering = ["due_date"]

    def get_permissions(self):
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), CanDeleteTask()]
        if self.action in ("update", "partial_update"):
            return [permissions.IsAuthenticated(), CanModifyTask()]
        return [permissions.IsAuthenticated(), IsProjectMemberForTask()]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_admin", False):
            return Task.objects.all()
        return (
            Task.objects.filter(project__owner=user)
            | Task.objects.filter(project__members=user)
        ).distinct()

    def perform_create(self, serializer):
        project = serializer.validated_data.get("project")
        user = self.request.user

        is_member = (
            getattr(user, "is_admin", False)
            or project.owner == user
            or project.members.filter(id=user.id).exists()
        )
        if not is_member:
            raise PermissionDenied("You are not a member of this project.")

        serializer.save(created_by=user)
