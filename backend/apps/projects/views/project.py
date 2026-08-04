from django.contrib.auth import get_user_model
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from apps.projects.filters import ProjectFilter
from apps.projects.models import Project
from apps.projects.permissions import (
    IsAdminPMOrTM,
    IsProjectMemberOrAdmin,
    IsProjectOwnerOrAdmin,
)
from apps.projects.serializers import ProjectSerializer
from apps.projects.services import (
    CreateProjectService,
    DeleteProjectService,
    UpdateProjectService,
)

User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectFilter

    # controls which porjects can this specific user even see
    def get_queryset(self):
        user = self.request.user
        base_queryset = Project.objects.select_related("owner").annotate(
            member_count=Count("members", distinct=True),
            task_count=Count("tasks", distinct=True),
        )
        if getattr(user, "is_admin", False) or getattr(user, "role", "") == "ADMIN":
            return base_queryset
        return (
            base_queryset.filter(owner=user)
            | base_queryset.filter(members=user)
            | base_queryset.filter(tasks__assignees=user)
        ).distinct()

    def get_permissions(self):
        if self.action == "create":
            return [IsAdminPMOrTM()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsProjectOwnerOrAdmin()]
        return [IsProjectMemberOrAdmin()]

    def perform_create(self, serializer):
        project = CreateProjectService.execute(
            user=self.request.user,
            name=self.request.data.get("name"),
            description=self.request.data.get("description", ""),
            department=self.request.data.get("department"),
        )
        serializer.instance = project

    def perform_update(self, serializer):
        project = UpdateProjectService.execute(
            project=serializer.instance,
            name=self.request.data.get("name"),
            description=self.request.data.get("description"),
            department=self.request.data.get("department"),
        )
        serializer.instance = project

    def perform_destroy(self, instance):
        DeleteProjectService.execute(project=instance)
