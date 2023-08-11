from rich.console import Console

console = Console()


def log(*args, **kwargs):
    console.print('[Ether]', *args, **kwargs)


def get_api_id(model):
    return getattr(model._meta, 'api_id', None) or f'{model._meta.model_name}s'
