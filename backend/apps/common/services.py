import logging
from typing import Any, Dict, Optional, Type

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.db import models, transaction
from rest_framework.exceptions import (
    APIException,
    NotFound,
    ValidationError,
)
from rest_framework.exceptions import (
    PermissionDenied as DRFPermissionDenied,
)
from rest_framework.serializers import Serializer

logger = logging.getLogger(__name__)


class BaseService:
    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def validate(self) -> None:
        pass

    def process(self) -> Any:
        raise NotImplementedError("Subclasses of BaseService must implement process().")

    @classmethod
    def execute(cls, *args: Any, **kwargs: Any) -> Any:
        if args:
            standard_names = ["request", "view"]
            for i, arg in enumerate(args):
                if i < len(standard_names):
                    kwargs.setdefault(standard_names[i], arg)
                elif isinstance(arg, Serializer):
                    kwargs.setdefault("serializer", arg)
                elif hasattr(arg, "model"):
                    kwargs.setdefault("queryset", arg)
                else:
                    kwargs.setdefault(f"arg_{i}", arg)

        if "request" in kwargs and "user" not in kwargs:
            kwargs["user"] = kwargs["request"].user

        instance = cls(**kwargs)

        instance.validate()

        try:
            with transaction.atomic():
                return instance.process()
        except (
            ValidationError,
            NotFound,
            DRFPermissionDenied,
            DjangoPermissionDenied,
            ObjectDoesNotExist,
        ):
            raise
        except Exception as exc:
            cls.log_error(cls.__name__, exc)
            raise APIException(
                "A technical error occurred in the service layer."
            ) from exc

    @classmethod
    def log_error(cls, service_name: str, exception: Exception) -> None:
        logger.error(
            f"Service Error in {service_name}: {str(exception)}", exc_info=True
        )

    def log_info(self, message: str) -> None:
        logger.info(f"[{self.__class__.__name__}] {message}")

    def get_object(self, model: Type[models.Model], **filters: Any) -> Any:
        try:
            return model.objects.get(**filters)
        except model.DoesNotExist:
            raise NotFound(f"{model.__name__} not found.")

    def get_object_or_none(
        self, model: Type[models.Model], **filters: Any
    ) -> Optional[Any]:
        try:
            return model.objects.get(**filters)
        except model.DoesNotExist:
            return None

    def get_queryset(
        self, model: Type[models.Model], **filters: Any
    ) -> models.QuerySet:
        return model.objects.filter(**filters)

    def check_permission(
        self, condition: bool, message: str = "Permission denied."
    ) -> None:
        if not condition:
            raise DRFPermissionDenied(message)

    def validate_serializer(
        self, serializer_class: Any, data: Dict[str, Any], **kwargs: Any
    ) -> Any:
        serializer = serializer_class(data=data, **kwargs)
        serializer.is_valid(raise_exception=True)
        return serializer

    def create_object(self, serializer: Any, **extra_fields: Any) -> Any:
        return serializer.save(**extra_fields)

    def update_object(
        self, instance: models.Model, data: Dict[str, Any], serializer_class: Any
    ) -> Any:
        serializer = serializer_class(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        updated_instance.refresh_from_db()
        return updated_instance

    def delete_object(self, instance: models.Model) -> None:
        try:
            instance.delete()
        except Exception as exc:
            self.log_error(self.__class__.__name__, exc)
            raise APIException("Failed to delete the object.")

    def log_warning(self, message: str) -> None:
        logger.warning(f"[{self.__class__.__name__}] {message}")
