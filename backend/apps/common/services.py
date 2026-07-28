import logging
import typing

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from rest_framework.exceptions import APIException, NotFound, ValidationError

logger = logging.getLogger(__name__)


class BaseService:

    def __init__(self, **kwargs: typing.Any) -> None:
        # Dynamically set all input parameters as instance attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def process(self) -> typing.Any:
        """Subclasses MUST override this method with their core logic."""
        raise NotImplementedError("Subclasses of BaseService must implement process().")

    @classmethod
    def execute(cls, **kwargs: typing.Any) -> typing.Any:
        """
        The main entry point called by Views.
        Example: GetCommentsService.execute(request=request, view=view, queryset=qs)
        """
        instance = cls(**kwargs)

        # Automatically wrap the action inside a safe database transaction
        try:
            with transaction.atomic():
                return instance.process()
        except (APIException, ObjectDoesNotExist, PermissionDenied):
            raise
        except Exception as exc:
            cls.log_error(cls.__name__, exc)
            raise APIException("An unexpected error occurred.") from exc
