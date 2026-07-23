from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.permissions import IsAdmin
from apps.users.serializers import UserDetailSerializer, UserListSerializer
from apps.users.service import UserService


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserService.get_all_users()
    permission_classes = [IsAuthenticated, IsAdmin]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action in ("retrieve", "partial_update"):
            return UserDetailSerializer
        return UserListSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        UserService.deactivate_user(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

