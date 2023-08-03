from rich.console import Console

console = Console()


def log(*args, **kwargs):
    console.print('[Ether]', *args, **kwargs)
