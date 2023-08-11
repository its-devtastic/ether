from django.apps import AppConfig

from .router import rest_router
from ..contenttypes import registry
from ..utils import log


class EtherRestConfig(AppConfig):
    name = 'ether.rest'
    initialized = False

    def ready(self):
        if not self.initialized:
            log(':building_construction:', 'Setting up REST routes')
            contenttypes = registry.entries()

            for [basename, contenttype] in contenttypes:
                rest_router.register(basename, contenttype.view_set)

            self.initialized = True
