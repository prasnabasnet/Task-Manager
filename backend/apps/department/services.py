from rest_framework.exceptions import NotFound, PermissionDenied

from apps.organization.models import Organization
from apps.projects.serializers import ProjectSerializer
from apps.shared.services import BaseService


class BaseDepartmentService(BaseService):
    def get_organization(self, pk, user):
        try:
            org = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found")

        if not getattr(user, "is_admin", False):
            is_owner = org.owner == user
            is_member = org.memberships.filter(user=user).exists()
            if not (is_owner or is_member):
                raise PermissionDenied("You are not a member of this organization")

        return org


class GetDepartmentService(BaseDepartmentService):
    def process(self):
        org = self.get_organization(self.organization_id, self.user)
        return org.departments.all()


class CreateDepartmentService(BaseDepartmentService):
    def process(self):
        org = self.get_organization(self.organization_id, self.user)
        return self.serializer.save(organizatoin=org)


class GetDepartmentProjectService(BaseService):
    def process(self):
        return self.departments.projects.all()


class CreateProjectService(BaseService):
    def process(self):
        user = self.user
        department = self.department

        if not (getattr(user, "is_admin", False) or getattr(user, "role", "") == "PM"):
            raise PermissionDenied("You are not authorized to create project")

        data = self.data.copy()
        data["department"] = department.pk
        serializer = ProjectSerializer(data=data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=user)
        return serializer.data
