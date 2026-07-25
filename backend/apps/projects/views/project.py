from django.contrib.auth import get_user_model
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError
from service_objects.errors import InvalidInputsError

from apps.projects.filters import ProjectFilter
from apps.projects.models import Project
from apps.projects.permissions import (
    IsAdminOrPM,
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

    def get_queryset(self):
        user = self.request.user
        base_queryset = Project.objects.select_related("owner").annotate(
            member_count=Count("members", distinct=True),
            task_count=Count("tasks", distinct=True),
        )
        if user.role == "ADMIN":
            return base_queryset
        return base_queryset.filter(owner=user) | base_queryset.filter(members=user)

    def get_permissions(self):
        if self.action == "create":
            return [IsAdminOrPM()]
        if self.action in ("update", "partial_update", "destroy"):
            return [IsProjectOwnerOrAdmin()]
        return [IsProjectMemberOrAdmin()]

    def perform_create(self, serializer):
        inputs = {**self.request.data, "user": self.request.user}
        try:
            project = CreateProjectService.execute(inputs)
        except InvalidInputsError as e:
            raise DRFValidationError(e.errors)
        serializer.instance = project

    def perform_update(self, serializer):
        inputs = {**self.request.data, "project": serializer.instance}
        try:
            project = UpdateProjectService.execute(inputs)
        except InvalidInputsError as e:
            raise DRFValidationError(e.errors)
        serializer.instance = project

    def perform_destroy(self, instance):
        DeleteProjectService.execute({"project": instance})
