from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True)


class TimestampMixin:
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)


class OwnerMixin:
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class OptionalOwnerMixin:
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


class SoftDeleteMixin:
    deleted = models.BooleanField(default=False)


class ContentModel(BaseModel, TimestampMixin, OptionalOwnerMixin, SoftDeleteMixin):
    class Meta:
        abstract = True
