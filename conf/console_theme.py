from rich.theme import Theme
from rich.console import Console

custom_theme = Theme({
    "warning": "yellow",
    "disaster": "bold red"
})

CONSOLE = Console(theme=custom_theme)