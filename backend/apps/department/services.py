from rest_framework.exceptions import NotFound, PermissionDenied
from apps.organization.models import Organization
from apps.projects.serializers import ProjectSerializer


class DepartmentService:
    @staticmethod
    def get_organization(pk, user):
        try:
            org = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found.")

        if not user.is_admin:
            is_owner = org.owner == user
            is_member = org.memberships.filter(user=user).exists()
            if not (is_owner or is_member):
                raise PermissionDenied("You are not a member of this organization.")
        return org

    @classmethod
    def get_departments(cls, organization_id, user):
        org = cls.get_organization(organization_id, user)
        return org.departments.all()

    @classmethod
    def create_department(cls, organization_id, user, serializer):
        org = cls.get_organization(organization_id, user)
        return serializer.save(organization=org)

    @staticmethod
    def get_department_projects(department):
        return department.projects.all()

    @staticmethod
    def create_project(department, user, data, request):
        if not (user.is_admin or user.role == "PM"):
            raise PermissionDenied("Only admins and project managers can create projects.")

        data = data.copy()
        data["department"] = department.pk
        serializer = ProjectSerializer(
            data=data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=user)
        return serializer.data
