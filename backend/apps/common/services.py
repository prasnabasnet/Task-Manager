import logging

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework.exceptions import APIException, NotFound, ValidationError

logger = logging.getLogger(__name__)


class BaseService:

    @classmethod
    def get_object(cls, model, **filters):
        try:
            return model.objects.get(**filters)
        except ObjectDoesNotExist:
            raise NotFound(
                f"{model.__name__} not found with {filters}"
            )

    @classmethod
    def get_object_or_none(cls, model, **filters):
        try:
            return model.objects.get(**filters)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_list(cls, model, **filters):
        return model.objects.filter(**filters)

    @staticmethod
    def check_permission(condition, message="You do not have permission to perform this action."):
        if not condition:
            raise PermissionDenied(message)

    @staticmethod
    def check_object_permission(user, obj, predicate, message="Permission denied for this object."):
        if not predicate(user, obj):
            raise PermissionDenied(message)

    @staticmethod
    def validate_serializer(serializer):
        serializer.is_valid(raise_exception=True)
        return serializer

    @classmethod
    def log_action(cls, action, **context):
        logger.info("Service action: %s | %s", action, context)

    @classmethod
    def log_error(cls, action, error, **context):
        logger.error("Service error in %s: %s | %s", action, error, context)

    @classmethod
    def safe_execute(cls, action, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (APIException, ObjectDoesNotExist, PermissionDenied):
            raise
        except Exception as exc:
            cls.log_error(action, exc)
            raise APIException("An unexpected error occurred.") from exc