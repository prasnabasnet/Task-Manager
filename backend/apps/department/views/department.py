from apps import department
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.department.serializers import DepartmentSerializer
from apps.projects.serializers import ProjectSerializer
from apps.users.permissions import IsAdminOrOrgOwner
from apps.department.services import DepartmentService


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrOrgOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return DepartmentService.get_departments(self.kwargs["oid"], self.request.user)

    def perform_create(self, serializer):
        DepartmentService.create_department(self.kwargs["oid"], self.request.user, serializer)

    @extend_schema(
        responses={200: ProjectSerializer(many=True)},
        summary="List projects in a department",
        description="Returns all projects associated with the specified department that the user has access to.",
    )
    @action(detail=True, methods=["get"], url_path="projects")
    def list_projects(self, request, oid=None, pk=None):
        department = self.get_object()
        projects = DepartmentService.get_department_projects(department)
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
        data = DepartmentService.create_project(
            department=department,
            user=request.user,
            data=request.data,
            request=request
        )
        return Response(data, status=201)

