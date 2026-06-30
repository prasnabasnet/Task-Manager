from django.contrib.auth import get_user_model
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.projects.models import Project, ProjectMember
from apps.projects.permissions import IsAdminOrPM, IsProjectMemberOrAdmin, IsProjectOwnerOrAdmin
from apps.projects.serializers import AddMemberSerializer, ProjectMemberSerializer, ProjectSerializer

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


class ProjectMemberListAddView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get_project(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return None

    def get(self, request, pk):
        project = self.get_project(pk)
        if not project:
            return Response(
                {'error': 'not_found', 'message': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role != 'ADMIN' and not project.members.filter(
            id=request.user.id
        ).exists() and project.owner != request.user:
            return Response(
                {'error': 'forbidden', 'message': 'You are not a member of this project.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        members = ProjectMember.objects.filter(project=project).select_related('user')
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        project = self.get_project(pk)
        if not project:
            return Response(
                {'error': 'not_found', 'message': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role != 'ADMIN' and project.owner != request.user:
            return Response(
                {'error': 'forbidden', 'message': 'Only the project owner or admin can add members.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        user = User.objects.get(id=user_id)

        if ProjectMember.objects.filter(project=project, user=user).exists():
            return Response(
                {'error': 'conflict', 'message': 'User is already a member of this project.'},
                status=status.HTTP_409_CONFLICT,
            )

        ProjectMember.objects.create(project=project, user=user)
        return Response(
            {'message': f'{user.email} added to {project.name} successfully.'},
            status=status.HTTP_201_CREATED,
        )


class ProjectMemberRemoveView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, uid):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(
                {'error': 'not_found', 'message': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role != 'ADMIN' and project.owner != request.user:
            return Response(
                {'error': 'forbidden', 'message': 'Only the project owner or admin can remove members.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            membership = ProjectMember.objects.get(project=project, user__id=uid)
        except ProjectMember.DoesNotExist:
            return Response(
                {'error': 'not_found', 'message': 'User is not a member of this project.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)