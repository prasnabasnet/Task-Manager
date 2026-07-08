from django.conf import settings
from django.db import models


# Create your models here.
class Department(models.Model):
    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.CASCADE,
        related_name="departments",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="headed_departments",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="departments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("organization", "name")  # no identical names

    def __str__(self):
        return f"{self.name} in {self.organization.name}"
