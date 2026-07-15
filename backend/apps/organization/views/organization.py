from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.organization.models import Organization
from apps.organization.permissions import IsAdminOrOwner
from apps.organization.serializers import OrganizationSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminOrOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_admin", False):
            return Organization.objects.all()
        return (
            Organization.objects.filter(
                Q(memberships__user=user)
                | Q(owner=user)
                | Q(departments__projects__members=user)
                | Q(departments__projects__owner=user)
            )
        ).distinct()
