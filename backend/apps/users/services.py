import logging

from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from apps.shared.services import BaseService
from apps.users.models import Profile
from apps.users.serializers import ProfileUpdateSerializer, UserRegisterSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterUserService(BaseService):
    def process(self):
        serializer = self.validate_serializer(UserRegisterSerializer, self.data)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return user, token


class AuthenticateUserService(BaseService):
    def validate(self):
        if not getattr(self, "email", None) or not getattr(self, "password", None):
            raise ValidationError("Email and password are required.")

    def process(self):
        request = getattr(self, "request", None)
        user = authenticate(request, username=self.email, password=self.password)

        if user is None:
            raise AuthenticationFailed("Invalid email or password.")

        token, _ = Token.objects.get_or_create(user=user)
        return user, token


class LogoutUserService(BaseService):
    def process(self):
        if self.request and self.request.auth:
            self.request.auth.delete()


class UpdateProfileService(BaseService):
    def process(self):
        profile, _ = Profile.objects.get_or_create(user=self.user)
        serializer = self.validate_serializer(
            ProfileUpdateSerializer, self.data, instance=profile, partial=True
        )
        serializer.save()

        self.user.refresh_from_db()
        return self.user


class DeactivateUserService(BaseService):
    def process(self):
        user = self.user
        user.is_active = False
        user.save(update_fields=["is_active"])
        return user


class GetAllUsersService(BaseService):
    def process(self):
        return User.objects.select_related("profile").all()
