from django.conf import settings
from django.db import models


class Project(models.Model):
    """Represents a project that contains tasks and members."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_projects',
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMember',
        related_name='member_projects',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.name


class ProjectMember(models.Model):
    """Through model linking users to projects with membership metadata."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_members',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships',
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')
        verbose_name = 'Project Member'
        verbose_name_plural = 'Project Members'

    def __str__(self):
        return f'{self.user} — {self.project}'