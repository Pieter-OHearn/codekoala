import random
from typing import Any, Callable, List
from rich.console import Console
from codekoala.koala_messages import KOALA_QUOTES


def format_output(suggestions: str) -> None:
    """Formats and displays the diff and suggestions."""
    console = Console()

    if suggestions:
        console.print(suggestions)
        console.print(random.choice(KOALA_QUOTES))
    else:
        console.print("[bold yellow]No suggestions found![/]")


def execute_with_spinner(command: Callable[..., Any], loading_messages: List[str], *args, **kwargs) -> Any:
    """Wraps a command execution with a loading spinner and returns the result."""
    console = Console()
    with console.status(random.choice(loading_messages), spinner="dots9"):
        result = command(*args, **kwargs)
    return result
