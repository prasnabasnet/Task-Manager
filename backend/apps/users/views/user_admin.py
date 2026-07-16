from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsAdmin
from apps.users.serializers import UserDetailSerializer, UserListSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("profile").all()
    permission_classes = [IsAuthenticated, IsAdmin]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action in ("retrieve", "partial_update"):
            return UserDetailSerializer
        return UserListSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
