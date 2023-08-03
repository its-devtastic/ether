from typing import Type

from django.db import models


class ContentType:
    """
    Content type base class.
    """
    pass


class ContentTypesRegistry:
    """
    Class for keeping a register of discovered content types.
    """
    _registry: dict[str, dict] = {}

    def register(self, api_id: str, model: Type[models.Model], contenttype: Type[ContentType]):
        """
        Register a content type under an API ID.
        """
        self._registry[api_id] = {'contenttype': contenttype, 'model': model}

    def get(self, api_id: str):
        """
        Returns the content type class and model class for a given API ID.
        """
        return self._registry.get(api_id)

    def entries(self):
        """
        Returns the entire registry.
        """
        return self._registry.items()

    def __len__(self):
        return len(self._registry)


# Create a default registry
registry = ContentTypesRegistry()


def register(model: Type[models.Model], api_id: str = None):
    api_id = api_id or f'{model.__name__.lower()}s'
    """
    Decorator for registering a content type.
    """

    def decorator(contenttype: Type[ContentType]):
        model._meta.api_id = api_id
        registry.register(api_id, model, contenttype)
        return contenttype

    return decorator
