from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.department.serializers import DepartmentSerializer
from apps.department.services import (
    CreateDepartmentService,
    CreateProjectService,
    GetDepartmentProjectService,
    GetDepartmentService,
)
from apps.projects.serializers import ProjectSerializer
from apps.users.permissions import IsAdminOrOrgOwner


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrOrgOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return GetDepartmentService.execute(
            organization_id=self.kwargs["oid"], user=self.request.user
        )

    def perform_create(self, serializer):
        return CreateDepartmentService.execute(
            organization_id=self.kwargs["oid"],
            user=self.request.user,
            data=serializer.validated_data,
        )

    @extend_schema(
        responses={200: ProjectSerializer(many=True)},
        summary="List projects in a department",
        description="Returns all projects associated with the specified department that the user has access to.",
    )
    @action(detail=True, methods=["get"], url_path="projects")
    def list_projects(self, request, oid=None, pk=None):
        department = self.get_object()
        projects = GetDepartmentProjectService.execute(
            department=department, user=request.user
        )
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ProjectSerializer,
        responses={201: ProjectSerializer},
        summary="Create project in a department",
        description="Creates a new project within the specified department. The department relationship is auto-injected.",
    )
    @action(detail=True, methods=["post"], url_path="projects")
    def create_project(self, request, oid=None, pk=None):
        department = self.get_object()
        project_data = CreateProjectService.execute(
            department=department, user=request.user, data=request.data, request=request
        )

        return Response(project_data, status=status.HTTP_201_CREATED)
