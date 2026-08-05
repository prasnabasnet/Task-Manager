from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.organization.models import Organization
from apps.organization.permissions import CanCreateOrganization, IsAdminOrOwner
from apps.organization.serializers import OrganizationSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminOrOwner()]
        if self.action == "create":
            return [CanCreateOrganization()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", "") == "SUPERADMIN" or getattr(user, "is_superuser", False):
            return Organization.objects.all()
        return (
            Organization.objects.filter(memberships__user=user)
            | Organization.objects.filter(owner=user)
            | Organization.objects.filter(departments__projects__members=user)
            | Organization.objects.filter(departments__projects__tasks__assignees=user)
        ).distinct()

