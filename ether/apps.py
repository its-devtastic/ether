from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

from .contenttypes import registry
from .utils import log


class EtherConfig(AppConfig):
    name = 'ether'
    initialized = False

    def ready(self):
        if not self.initialized:
            log(':mag:', 'Discovering content types...')
            autodiscover_modules('contenttypes')
            log(':white_check_mark:', '[green]Found {0} contenttypes[/green]'.format(len(registry)))

            self.initialized = True
