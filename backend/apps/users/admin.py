from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.users.models import Profile, User


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"
    fields = ("display_name", "avatar_url", "bio", "timezone")


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "date_joined",
    )
    list_editable = ("is_active",)
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("role", "is_active", "is_staff")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = ((None, {"fields": ("email", "password1", "password2", "role")}),)

    ordering = ("email",)

    def get_inline_instances(self, request, obj=None):
        # Don't show the Profile inline on the "add user" form, since
        # the Profile doesn't exist until the signal fires on save.
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


admin.site.register(User, UserAdmin)
