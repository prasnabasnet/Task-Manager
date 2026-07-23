from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token

from apps.users.serializers import ProfileUpdateSerializer, UserRegisterSerializer

User = get_user_model()


class UserService:
    """Service object encapsulating business logic for User operations."""

    @staticmethod
    def register_user(data):
        """Registers a new user and returns (user, token)."""
        serializer = UserRegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return user, token

    @staticmethod
    def authenticate_user(email, password, request=None):
        """Authenticates user with email & password.

        Returns ((user, token), None) on success or (None, error_message) on failure.
        """
        if not email or not password:
            return None, "Email and password are required."

        user = authenticate(request, username=email, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return (user, token), None

        return None, "Invalid email or password."

    @staticmethod
    def logout_user(user):
        """Deletes authentication token for the specified user."""
        Token.objects.filter(user=user).delete()

    @staticmethod
    def update_profile(user, data):
        """Updates profile for the specified user."""
        profile = getattr(user, "profile", None)
        if profile is None:
            from apps.users.models import Profile

            profile, _ = Profile.objects.get_or_create(user=user)

        serializer = ProfileUpdateSerializer(profile, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user.refresh_from_db()
        return user

    @staticmethod
    def deactivate_user(user):
        """Deactivates / soft-deletes a user."""
        user.is_active = False
        user.save(update_fields=["is_active"])
        return user

    @staticmethod
    def get_all_users():
        """Returns queryset of all users with profile pre-fetched."""
        return User.objects.select_related("profile").all()
