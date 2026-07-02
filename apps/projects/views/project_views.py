from django.contrib.auth import get_user_model
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.projects.models import Project
from apps.projects.permissions import IsAdminOrPM, IsProjectMemberOrAdmin, IsProjectOwnerOrAdmin
from apps.projects.serializers import ProjectSerializer

User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['owner']

    def get_queryset(self):
        user = self.request.user
        base_queryset = Project.objects.select_related('owner').annotate(
            member_count=Count('members', distinct=True)
        )
        if user.role == 'ADMIN':
            return base_queryset
        return base_queryset.filter(owner=user) | base_queryset.filter(members=user)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsAdminOrPM()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsProjectOwnerOrAdmin()]
        return [IsAuthenticated(), IsProjectMemberOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)