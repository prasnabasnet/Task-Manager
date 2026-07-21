from django.contrib.auth import get_user_model
from rest_framework import serializers, status, views
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.projects.models import Project, ProjectMember
from apps.projects.serializers import AddMemberSerializer, ProjectMemberSerializer

User = get_user_model()


class AddMemberResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class ProjectMemberListAddView(views.APIView):
    def get_project(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return None

    @extend_schema(
        responses={200: ProjectMemberSerializer(many=True)},
        summary="List project members",
        description="Returns all members of the specified project.",
    )
    def get(self, request, pk):
        project = self.get_project(pk)
        if not project:
            return Response(
                {"error": "not_found", "message": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            request.user.role != "ADMIN"
            and not project.members.filter(id=request.user.id).exists()
            and project.owner != request.user
        ):
            return Response(
                {
                    "error": "forbidden",
                    "message": "You are not a member of this project.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        members = ProjectMember.objects.filter(project=project).select_related("user")
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=AddMemberSerializer,
        responses={201: AddMemberResponseSerializer},
        summary="Add member to project",
        description="Adds a user to a project's members list.",
    )
    def post(self, request, pk):
        project = self.get_project(pk)
        if not project:
            return Response(
                {"error": "not_found", "message": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role != "ADMIN" and project.owner != request.user:
            return Response(
                {
                    "error": "forbidden",
                    "message": "Only the project owner or admin can add members.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        user = User.objects.get(id=user_id)

        if ProjectMember.objects.filter(project=project, user=user).exists():
            return Response(
                {
                    "error": "conflict",
                    "message": "User is already a member of this project.",
                },
                status=status.HTTP_409_CONFLICT,
            )

        ProjectMember.objects.create(project=project, user=user)
        return Response(
            {"message": f"{user.email} added to {project.name} successfully."},
            status=status.HTTP_201_CREATED,
        )


class ProjectMemberRemoveView(views.APIView):
    @extend_schema(
        responses={204: None},
        summary="Remove member from project",
        description="Removes a user from a project's members list.",
    )
    def delete(self, request, pk, uid):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response(
                {"error": "not_found", "message": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user.role != "ADMIN" and project.owner != request.user:
            return Response(
                {
                    "error": "forbidden",
                    "message": "Only the project owner or admin can remove members.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            membership = ProjectMember.objects.get(project=project, user__id=uid)
        except ProjectMember.DoesNotExist:
            return Response(
                {
                    "error": "not_found",
                    "message": "User is not a member of this project.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
