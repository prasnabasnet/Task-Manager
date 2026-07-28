from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.common.services import (
    BaseService,
)
from apps.projects.models import Project, ProjectMember
from apps.projects.utils import send_project_notification

User = get_user_model()


class CreateProjectService(BaseService):
    def process(self):
        name = getattr(self, "name", None)
        department = getattr(self, "department", None)

        if not name:
            raise ValidationError({"name": "This field is required."})
        if not department:
            raise ValidationError({"department": "This field is required."})

        project = Project.objects.create(
            owner=self.user,
            name=name,
            description=getattr(self, "description", "") or "",
            department_id=department,
        )

        send_project_notification(
            project.id,
            {
                "type": "project_created",
                "project_id": project.id,
                "project_name": project.name,
                "message": f'Project "{project.name}" was created',
                "triggered_by": self.user.email,
            },
        )

        return project


class UpdateProjectService(BaseService):
    def process(self):
        project = self.project
        for field, model_field in (
            ("name", "name"),
            ("description", "description"),
            ("department", "department_id"),
        ):
            value = getattr(self, field, None)
            if value not in (None, ""):
                setattr(project, model_field, value)
        project.save()

        send_project_notification(
            project.id,
            {
                "type": "project_updated",
                "project_id": project.id,
                "project_name": project.name,
                "message": f'Project "{project.name}" was updated',
                "triggered_by": project.owner.email,
            },
        )

        return project


class DeleteProjectService(BaseService):
    def process(self):
        project_id = self.project.id
        project_name = self.project.name
        self.project.delete()

        send_project_notification(
            project_id,
            {
                "type": "project_deleted",
                "project_id": project_id,
                "project_name": project_name,
                "message": f'Project "{project_name}" was deleted',
            },
        )


class AddProjectMemberService(BaseService):
    def process(self):
        project = self.project
        requesting_user = self.requesting_user

        if requesting_user.role != "ADMIN" and project.owner != requesting_user:
            raise PermissionDenied("Only the project owner or admin can add members.")

        try:
            user_to_add = User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            raise NotFound("User not found.")

        if ProjectMember.objects.filter(project=project, user=user_to_add).exists():
            raise ValidationError("User is already a member of this project.")

        membership = ProjectMember.objects.create(project=project, user=user_to_add)

        send_project_notification(
            project.id,
            {
                "type": "member_added",
                "project_id": project.id,
                "project_name": project.name,
                "user_email": user_to_add.email,
                "message": f'{user_to_add.email} was added to "{project.name}"',
            },
        )

        return membership


class RemoveProjectMemberService(BaseService):
    def process(self):
        project = self.project
        requesting_user = self.requesting_user

        if requesting_user.role != "ADMIN" and project.owner != requesting_user:
            raise PermissionDenied(
                "Only the project owner or admin can remove members."
            )

        try:
            membership = ProjectMember.objects.get(
                project=project, user__id=self.user_id
            )
        except ProjectMember.DoesNotExist:
            raise NotFound("User is not a member of this project.")

        user_email = membership.user.email
        membership.delete()

        send_project_notification(
            project.id,
            {
                "type": "member_removed",
                "project_id": project.id,
                "project_name": project.name,
                "user_email": user_email,
                "message": f'{user_email} was removed from "{project.name}"',
            },
        )
