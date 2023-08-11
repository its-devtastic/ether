from django.apps import AppConfig
from rest_framework.viewsets import ModelViewSet

from .exceptions import Conflict
from .router import rest_router
from .serializers import JsonApiV11ModelSerializer
from ..contenttypes import registry
from ..utils import log


class EtherRestConfig(AppConfig):
    name = 'ether.rest'
    initialized = False

    def ready(self):
        if not self.initialized:
            log(':building_construction:', 'Setting up REST routes')
            contenttypes = registry.entries()

            for [basename, config] in contenttypes:
                class Serializer(JsonApiV11ModelSerializer):
                    class Meta:
                        model = config['model']
                        fields = '__all__'

                class ViewSet(ModelViewSet):
                    queryset = config['model'].objects.all()
                    serializer_class = Serializer

                    def perform_create(self, serializer):
                        if serializer.initial_data.get('data', {}).get('type') != basename:
                            raise Conflict(detail='Type does not match base name')
                        return super().perform_create(serializer)

                rest_router.register(basename, ViewSet)

            self.initialized = True