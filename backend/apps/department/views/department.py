from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.organization.models import Organization
from apps.department.serializers import DepartmentSerializer
from apps.projects.serializers import ProjectSerializer
from apps.users.permissions import IsAdminOrOrgOwner


def get_org(pk, user):
    try:
        org = Organization.objects.get(pk=pk)
    except Organization.DoesNotExist:
        raise NotFound("Organization not found.")

    if not user.is_admin:
        is_owner = org.owner == user
        is_member = org.memberships.filter(user=user).exists()
        is_project_member = org.departments.filter(projects__members=user).exists()
        is_project_owner = org.departments.filter(projects__owner=user).exists()
        if not (is_owner or is_member or is_project_member or is_project_owner):
            raise PermissionDenied("You are not a member of this organization.")
    return org


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrOrgOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        org = get_org(self.kwargs["oid"], user)
        if getattr(user, "is_admin", False) or org.owner == user or org.memberships.filter(user=user).exists():
            return org.departments.all()
        from django.db.models import Q
        return org.departments.filter(Q(projects__members=user) | Q(projects__owner=user)).distinct()

    def perform_create(self, serializer):
        org = get_org(self.kwargs["oid"], self.request.user)
        serializer.save(organization=org)

    @extend_schema(
        methods=["GET"],
        responses={200: ProjectSerializer(many=True)},
        summary="List projects in a department",
        description="Returns all projects associated with the specified department that the user has access to.",
    )
    @extend_schema(
        methods=["POST"],
        request=ProjectSerializer,
        responses={201: ProjectSerializer},
        summary="Create project in a department",
        description="Creates a new project within the specified department. The department relationship is auto-injected.",
    )
    @action(detail=True, methods=["get", "post"])
    def projects(self, request, oid=None, pk=None):
        department = self.get_object()
        if request.method == "POST":
            if not (request.user.is_admin or request.user.role == "PM"):
                raise PermissionDenied("Only admins and project managers can create projects.")
            
            data = request.data.copy()
            data["department"] = department.pk
            serializer = ProjectSerializer(
                data=data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)

        projects = department.projects.all()
        if not request.user.is_admin:
            org = department.organization
            is_org_owner = org.owner == request.user
            is_dept_head = department.head == request.user
            if not (is_org_owner or is_dept_head):
                from django.db.models import Q
                projects = projects.filter(Q(owner=request.user) | Q(members=request.user)).distinct()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)
