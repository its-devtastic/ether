from typing import Type

from django.db import models
from rest_framework.serializers import BaseSerializer

from .registry import registry
from .rest.serializers import JsonApiV11ModelSerializer
from .rest.viewsets import JsonApiModelViewSet
from .utils import get_api_id


class ContentType:
    """
    Content type base class.
    """
    api_id: str
    model: Type[models.Model] = None
    serializer_class: Type[BaseSerializer] = None

    def __init__(self, api_id=None):
        self.api_id = api_id or get_api_id(self.model)

        self.model._meta.api_id = self.api_id

    @property
    def serializer_class(self):
        class Serializer(JsonApiV11ModelSerializer):
            class Meta:
                model = self.model
                fields = '__all__'

        return Serializer

    @property
    def view_set(self):
        class ViewSet(JsonApiModelViewSet):
            serializer_class = self.serializer_class
            queryset = self.model.objects.all()
            api_id = self.api_id

        return ViewSet


def register(api_id: str = None):
    """
    Decorator for registering a content type.
    """

    def decorator(content_type_model: Type[ContentType]):
        content_type = content_type_model(api_id=api_id)

        registry.register(content_type.api_id, content_type)

        return content_type_model

    return decorator
