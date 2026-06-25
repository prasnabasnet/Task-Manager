from django.contrib.auth import get_user_model
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Project, ProjectMember
from .permissions import IsAdminOrPM, IsProjectMemberOrAdmin, IsProjectOwnerOrAdmin
from .serializers import AddMemberSerializer, ProjectMemberSerializer, ProjectSerializer

User = get_user_model()


class ProjectListCreateView(generics.ListCreateAPIView):
    """List all accessible projects or create a new project."""

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all projects for admin, or only owned/member projects for others."""
        user = self.request.user
        if user.role == 'ADMIN':
            return Project.objects.all()
        return Project.objects.filter(
            owner=user
        ) | Project.objects.filter(members=user)

    def get_permissions(self):
        """Only Admin or PM can create a project."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrPM()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Set the owner to the currently logged-in user."""
        serializer.save(owner=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a project."""

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectMemberOrAdmin]

    def get_queryset(self):
        """Return all projects for admin, or only accessible projects for others."""
        user = self.request.user
        if user.role == 'ADMIN':
            return Project.objects.all()
        return Project.objects.filter(
            owner=user
        ) | Project.objects.filter(members=user)

    def get_permissions(self):
        """Only owner or admin can update or delete."""
        if self.request.method in ('PATCH', 'DELETE'):
            return [IsAuthenticated(), IsProjectOwnerOrAdmin()]
        return [IsAuthenticated(), IsProjectMemberOrAdmin()]

    def destroy(self, request, *args, **kwargs):
        """Delete a project and return 204 No Content."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectMemberListAddView(views.APIView):
    """List all members of a project or add a new member."""

    permission_classes = [IsAuthenticated]

    def get_project(self, pk):
        """Return project or None if not found."""
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return None

    def get(self, request, pk):
        """List all members of a project."""
        project = self.get_project(pk)
        if not project:
            return Response(
                {'error': 'not_found', 'message': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if user is a member or admin
        if request.user.role != 'ADMIN' and not project.members.filter(
            id=request.user.id
        ).exists() and project.owner != request.user:
            return Response(
                {'error': 'forbidden', 'message': 'You are not a member of this project.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        members = ProjectMember.objects.filter(project=project)
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        """Add a new member to a project."""
        project = self.get_project(pk)
        if not project:
            return Response(
                {'error': 'not_found', 'message': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only owner or admin can add members
        if request.user.role != 'ADMIN' and project.owner != request.user:
            return Response(
                {'error': 'forbidden', 'message': 'Only the project owner or admin can add members.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        user = User.objects.get(id=user_id)

        # Check for duplicate membership
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
    """Remove a member from a project."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, uid):
        """Remove a member from a project."""
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(
                {'error': 'not_found', 'message': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only owner or admin can remove members
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