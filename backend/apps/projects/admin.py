from django.contrib import admin

from apps.projects.models import Project, ProjectMember


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "department", "created_at"]
    search_fields = ["name", "owner__email"]
    list_filter = ["department", "created_at"]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ["project", "user", "joined_at"]
    search_fields = ["project__name", "user__email"]
    list_filter = ["joined_at"]
