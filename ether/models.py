from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True)


class TimestampMixin:
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)


class OwnerMixin:
    class Meta:
        abstract = True

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class OptionalOwnerMixin:
    class Meta:
        abstract = True

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


class SoftDeleteMixin:
    class Meta:
        abstract = True

    deleted = models.BooleanField(default=False)


class ContentModel(BaseModel, TimestampMixin, OptionalOwnerMixin, SoftDeleteMixin):
    class Meta:
        abstract = True
