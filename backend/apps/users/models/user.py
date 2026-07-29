from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users.models.usermanager import UserManager


class RoleChoices(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    PROJECT_MANAGER = "PM", "Project Manager"
    TEAM_MEMBER = "TM", "Team Member"


class User(AbstractUser):
    objects = UserManager()

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=15, choices=RoleChoices.choices, default=RoleChoices.TEAM_MEMBER
    )

    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ["username", "role"]
    REQUIRED_FIELDS = ("username",)

    @property
    def is_admin(self):
        return self.role == RoleChoices.ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.email})"
