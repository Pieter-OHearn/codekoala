from typing import List
from rich.console import Console
from rich.table import Table

def format_output(diff: str, suggestions: str) -> None:
    """Formats and displays the diff and suggestions."""
    console = Console()

    if suggestions:
        table = Table(title="Review Suggestions")
        console.print("[bold Green]Review Suggestions[/]")
        console.print(suggestions)
    else:
        console.print("[bold yellow]No suggestions found![/]")
