from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import PermissionDenied

from apps.comments.models import Comment
from apps.comments.permissions import IsProjectMember

APP_LABEL_MAP = {
    "organization": "organization",
    "project": "projects",
    "task": "tasks",
}


class CommentService:
    @staticmethod
    def get_comments(request, view, queryset):
        target_type = request.query_params.get("target_type")
        target_id = request.query_params.get("target_id")
        parent_id = request.query_params.get("parent")

        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id)
            except Comment.DoesNotExist:
                return queryset.none()

            permission = IsProjectMember()
            if not permission.has_object_permission(request, view, parent_comment):
                raise PermissionDenied()
            return queryset.filter(parent_id=parent_id)

        if target_type and target_id:
            app_label = APP_LABEL_MAP.get(target_type)
            if not app_label:
                return queryset.none()

            try:
                ct = ContentType.objects.get(app_label=app_label, model=target_type)
                target_obj = ct.model_class().objects.get(id=target_id)
            except Exception:
                return queryset.none()

            permission = IsProjectMember()
            if not permission.has_object_permission(request, view, target_obj):
                raise PermissionDenied()

            return queryset.filter(
                content_type=ct, object_id=target_id, parent__isnull=True
            )

        return queryset.filter(author=request.user, parent__isnull=True)

    @staticmethod
    def create_comment(request, view, serializer):
        content_type = serializer.validated_data.get("content_type")
        target_id = serializer.validated_data.get("target_id")

        target_obj = content_type.model_class().objects.get(id=target_id)
        permission = IsProjectMember()
        if not permission.has_object_permission(request, view, target_obj):
            raise PermissionDenied()

        return serializer.save(
            author=request.user, content_type=content_type, object_id=target_id
        )
