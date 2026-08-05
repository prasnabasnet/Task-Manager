from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar_url", "bio", "display_name"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Used only on the /auth/me/ PATCH endpoint. Cannot touch email or password."""

    class Meta:
        model = Profile
        fields = ["avatar_url", "bio", "display_name"]


class UserRegisterSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["email", "username", "password", "organization_name"]

    def create(self, validated_data):
        validated_data.pop("organization_name", None)
        validated_data["role"] = "ORG_ADMIN"
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "date_joined",
            "is_active",
            "profile",
        ]
        read_only_fields = ["id", "email", "date_joined"]


class UserListSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "role", "date_joined", "profile"]
        read_only_fields = ["id", "email", "date_joined"]
