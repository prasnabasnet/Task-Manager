from django.contrib.auth import get_user_model
from rest_framework import serializers, status, views, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.users.serializers import (
    ProfileUpdateSerializer,
    UserDetailSerializer,
    UserRegisterSerializer,
)
from apps.users.service import UserService

User = get_user_model()


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={"input_type": "password"})


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UserDetailSerializer()


class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class RegisterView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        user, token = UserService.register_user(request.data)
        return Response(
            {"user": UserDetailSerializer(user).data, "token": token.key},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    request=LoginRequestSerializer,
    responses={200: LoginResponseSerializer},
    summary="User login",
    description="Authenticates user by email and password, returning an auth token.",
)
class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        (result, error) = UserService.authenticate_user(
            email, password, request=request
        )
        if error:
            status_code = (
                status.HTTP_400_BAD_REQUEST
                if "required" in error
                else status.HTTP_401_UNAUTHORIZED
            )
            return Response({"error": error}, status=status_code)

        user, token = result
        return Response(
            {"token": token.key, "user": UserDetailSerializer(user).data},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    request=None,
    responses={200: LogoutResponseSerializer},
    summary="User logout",
    description="Deletes the current authentication token.",
)
class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        UserService.logout_user(request.user)
        return Response(
            {"message": "Successfully logged out."}, status=status.HTTP_200_OK
        )


@extend_schema(tags=["User Profile"])
class MeView(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserDetailSerializer},
        summary="Retrieve user profile",
        description="Returns details of the currently logged-in user.",
    )
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ProfileUpdateSerializer,
        responses={200: UserDetailSerializer},
        summary="Update user profile",
        description="Updates the profile fields of the currently logged-in user.",
    )
    def patch(self, request):
        """Updates profile fields only. Email, username, password, role are untouchable here."""
        user = UserService.update_profile(request.user, request.data)
        return Response(
            UserDetailSerializer(user).data, status=status.HTTP_200_OK
        )

