from django.contrib.auth import authenticate, get_user_model
from rest_framework import status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.users.serializers import (
    ProfileUpdateSerializer,
    UserDetailSerializer,
    UserRegisterSerializer,
)

User = get_user_model()


class RegisterView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"user": UserDetailSerializer(user).data, "token": token.key},
            status=status.HTTP_201_CREATED,
        )


class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(request, username=email, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {"token": token.key, "user": UserDetailSerializer(user).data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(
            {"message": "Successfully logged out."}, status=status.HTTP_200_OK
        )


class MeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Updates profile fields only. Email, username, password, role are untouchable here."""
        profile = request.user.profile
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            UserDetailSerializer(request.user).data, status=status.HTTP_200_OK
        )
