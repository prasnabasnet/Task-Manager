"""
Base service layer for the Task Manager project.

Every app-specific service can import and extend ``BaseService`` to inherit
common utilities (logging, error handling, permission checks, etc.).

Usage::

    from apps.common.services import BaseService

    class UserService(BaseService):
        @classmethod
        def get_user(cls, user_id):
            return cls.get_object(User, pk=user_id)
"""

import logging

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework.exceptions import APIException, NotFound, ValidationError

logger = logging.getLogger(__name__)


class BaseService:
    """
    Lightweight base class for all service objects.

    It does **not** inherit from ``service_objects.services.Service`` so that
    apps can use either the simple static/class-method pattern *or* the
    ``service_objects`` form — both can extend ``BaseService`` (or mix it in).
    """

    # ------------------------------------------------------------------
    # Object retrieval helpers
    # ------------------------------------------------------------------
    @classmethod
    def get_object(cls, model, **filters):
        """Fetch a single object or raise ``NotFound``."""
        try:
            return model.objects.get(**filters)
        except ObjectDoesNotExist:
            raise NotFound(
                f"{model.__name__} not found with {filters}"
            )

    @classmethod
    def get_object_or_none(cls, model, **filters):
        """Fetch a single object or return ``None`` (no exception)."""
        try:
            return model.objects.get(**filters)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_list(cls, model, **filters):
        """Return a filtered queryset (empty if nothing matches)."""
        return model.objects.filter(**filters)

    # ------------------------------------------------------------------
    # Permission helpers
    # ------------------------------------------------------------------
    @staticmethod
    def check_permission(condition, message="You do not have permission to perform this action."):
        """Raise ``PermissionDenied`` if *condition* is falsy."""
        if not condition:
            raise PermissionDenied(message)

    @staticmethod
    def check_object_permission(user, obj, predicate, message="Permission denied for this object."):
        """
        Run *predicate(user, obj)* and raise ``PermissionDenied`` when it
        returns ``False``.
        """
        if not predicate(user, obj):
            raise PermissionDenied(message)

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    @staticmethod
    def validate_serializer(serializer):
        """Validate a DRF serializer, raising ``ValidationError`` on failure."""
        serializer.is_valid(raise_exception=True)
        return serializer

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------
    @classmethod
    def log_action(cls, action, **context):
        """Log a service action with optional structured context."""
        logger.info("Service action: %s | %s", action, context)

    @classmethod
    def log_error(cls, action, error, **context):
        """Log an error that occurred during a service action."""
        logger.error("Service error in %s: %s | %s", action, error, context)

    # ------------------------------------------------------------------
    # Error handling wrapper
    # ------------------------------------------------------------------
    @classmethod
    def safe_execute(cls, action, func, *args, **kwargs):
        """
        Execute *func* inside a try/except block.

        Returns the result on success or re-raises as a generic
        ``APIException`` on unexpected errors (after logging).
        """
        try:
            return func(*args, **kwargs)
        except (APIException, ObjectDoesNotExist, PermissionDenied):
            raise
        except Exception as exc:  # noqa: BLE001 — intentional broad catch
            cls.log_error(action, exc)
            raise APIException("An unexpected error occurred.") from exc
