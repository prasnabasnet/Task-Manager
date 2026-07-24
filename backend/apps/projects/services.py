from django import forms
from service_objects.services import Service

from apps.projects.models import Project, ProjectMember


class CreateProjectService(Service):
    name = forms.CharField(max_length=255)
    description = forms.CharField(required=False, widget=forms.Textarea)
    department_id = forms.IntegerField(required=False)

    def process(self):
        return Project.objects.create(
            owner=self.user,
            name=self.cleaned_data["name"],
            description=self.cleaned_data.get("description", ""),
            department_id=self.cleaned_data.get("department_id"),
        )


class UpdateProjectService(Service):
    name = forms.CharField(max_length=255, required=False)
    description = forms.CharField(required=False, widget=forms.Textarea)
    department_id = forms.IntegerField(required=False)

    def process(self):
        for field in ("name", "description", "department_id"):
            value = self.cleaned_data.get(field)
            if value not in (None, ""):
                setattr(self.project, field, value)
        self.project.save()
        return self.project


class DeleteProjectService(Service):
    def process(self):
        self.project.delete()


class AddProjectMemberService(Service):
    user_id = forms.IntegerField()

    def process(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        if (
            self.requesting_user.role != "ADMIN"
            and self.project.owner != self.requesting_user
        ):
            raise forms.ValidationError(
                "Only the project owner or admin can add members."
            )

        user_to_add = User.objects.get(id=self.cleaned_data["user_id"])

        if ProjectMember.objects.filter(
            project=self.project, user=user_to_add
        ).exists():
            raise forms.ValidationError("User is already a member of this project.")

        return ProjectMember.objects.create(project=self.project, user=user_to_add)


class RemoveProjectMemberService(Service):
    user_id = forms.IntegerField()

    def process(self):
        if (
            self.requesting_user.role != "ADMIN"
            and self.project.owner != self.requesting_user
        ):
            raise forms.ValidationError(
                "Only the project owner or admin can remove members."
            )

        try:
            membership = ProjectMember.objects.get(
                project=self.project, user__id=self.cleaned_data["user_id"]
            )
        except ProjectMember.DoesNotExist:
            raise forms.ValidationError("User is not a member of this project.")

        membership.delete()
