from django import forms
from django.contrib.auth import get_user_model
from service_objects.fields import ModelField
from service_objects.services import Service

from apps.projects.models import Project, ProjectMember

User = get_user_model()


class CreateProjectService(Service):
    user = ModelField(User)
    name = forms.CharField(max_length=255)
    description = forms.CharField(required=False, widget=forms.Textarea)
    department = forms.IntegerField()

    def process(self):
        return Project.objects.create(
            owner=self.cleaned_data["user"],
            name=self.cleaned_data["name"],
            description=self.cleaned_data.get("description", ""),
            department_id=self.cleaned_data["department"],
        )


class UpdateProjectService(Service):
    project = ModelField(Project)
    name = forms.CharField(max_length=255, required=False)
    description = forms.CharField(required=False, widget=forms.Textarea)
    department = forms.IntegerField(required=False)

    def process(self):
        project = self.cleaned_data["project"]
        for field, model_field in (
            ("name", "name"),
            ("description", "description"),
            ("department", "department_id"),
        ):
            value = self.cleaned_data.get(field)
            if value not in (None, ""):
                setattr(project, model_field, value)
        project.save()
        return project


class DeleteProjectService(Service):
    project = ModelField(Project)

    def process(self):
        self.cleaned_data["project"].delete()


class AddProjectMemberService(Service):
    project = ModelField(Project)
    requesting_user = ModelField(User)
    user_id = forms.IntegerField()

    def process(self):
        project = self.cleaned_data["project"]
        requesting_user = self.cleaned_data["requesting_user"]

        if requesting_user.role != "ADMIN" and project.owner != requesting_user:
            raise forms.ValidationError(
                "Only the project owner or admin can add members."
            )

        user_to_add = User.objects.get(id=self.cleaned_data["user_id"])

        if ProjectMember.objects.filter(project=project, user=user_to_add).exists():
            raise forms.ValidationError("User is already a member of this project.")

        return ProjectMember.objects.create(project=project, user=user_to_add)


class RemoveProjectMemberService(Service):
    project = ModelField(Project)
    requesting_user = ModelField(User)
    user_id = forms.IntegerField()

    def process(self):
        project = self.cleaned_data["project"]
        requesting_user = self.cleaned_data["requesting_user"]

        if requesting_user.role != "ADMIN" and project.owner != requesting_user:
            raise forms.ValidationError(
                "Only the project owner or admin can remove members."
            )

        try:
            membership = ProjectMember.objects.get(
                project=project, user__id=self.cleaned_data["user_id"]
            )
        except ProjectMember.DoesNotExist:
            raise forms.ValidationError("User is not a member of this project.")

        membership.delete()
