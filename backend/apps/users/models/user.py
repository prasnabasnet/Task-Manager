from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users.models.usermanager import UserManager


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    PROJECT_MANAGER = "PM", "Project Manager"
    TEAM_MEMBER = "TM", "Team Member"


class User(AbstractUser):
    objects = UserManager()

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=15, choices=Role.choices, default=Role.TEAM_MEMBER
    )
    username = models.CharField(max_length=150, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "role"]

    @property
    def is_admin(self):
        return self.role == Role.ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.email})"
