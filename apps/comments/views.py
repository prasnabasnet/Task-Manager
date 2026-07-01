from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

from apps.comments.models import Comment
from apps.comments.serializers import CommentSerializer
from apps.comments.permissions import IsProjectMember, IsCommentAuthorOrAdmin


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated, IsProjectMember]

        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes.append(IsCommentAuthorOrAdmin)

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = self.queryset

        # For detail views, don't restrict the queryset to the user's authored comments.
        # This allows permissions (like IsProjectMember and IsCommentAuthorOrAdmin) to check 
        # project membership and author permissions on the specific object, yielding 403 instead of 404.
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return queryset

        target_type = self.request.query_params.get('target_type')
        target_id = self.request.query_params.get('target_id')
        parent_id = self.request.query_params.get('parent')

        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id)
            except Comment.DoesNotExist:
                return queryset.none()

            permission = IsProjectMember()
            if not permission.has_object_permission(self.request, self, parent_comment):
                self.permission_denied(self.request)
            return queryset.filter(parent_id=parent_id)

        if target_type and target_id:
            app_label = 'projects' if target_type == 'project' else 'tasks'
            try:
                ct = ContentType.objects.get(app_label=app_label, model=target_type)
                target_obj = ct.model_class().objects.get(id=target_id)
            except Exception:
                return queryset.none()

            permission = IsProjectMember()
            if not permission.has_object_permission(self.request, self, target_obj):
                self.permission_denied(self.request)

            return queryset.filter(content_type=ct, object_id=target_id, parent__isnull=True)

        return queryset.filter(author=self.request.user, parent__isnull=True)

    def perform_create(self, serializer):
        content_type = serializer.validated_data.get('content_type')
        target_id = serializer.validated_data.get('target_id')

        target_obj = content_type.model_class().objects.get(id=target_id)
        permission = IsProjectMember()
        if not permission.has_object_permission(self.request, self, target_obj):
            self.permission_denied(self.request)

        serializer.save(
            author=self.request.user,
            content_type=content_type,
            object_id=target_id
        )