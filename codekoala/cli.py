import click
from typing import Optional
from rich.console import Console
from git import Repo
import pyperclip

from codekoala.koala_messages import KOALA_COMMIT_LOADING_MESSAGES, KOALA_REVIEW_LOADING_MESSAGES
from codekoala.verify_ollama import verify_ollama_setup
from codekoala.git_integration import get_repo, get_diff, GitIntegrationError
from codekoala.review_engine import (
    COMMIT_MESSAGE_SYSTEM_PROMPT,
    get_local_llm_code_suggestions,
    get_local_llm_commit_message,
    prepare_llm_commit_message_prompt,
)
from codekoala.formatter import format_output, execute_with_spinner
from codekoala.config import set_config, load_config


@click.group()
def cli():
    """CodeKoala CLI - LLM-powered code review."""
    pass


@click.command()
@click.option("--branch", default=None, help="Branch to compare against")
@click.option("--staged", is_flag=True, help="Only review staged changes")
def review_code(branch: Optional[str], staged: bool) -> None:
    """Reviews code changes before committing, comparing with a branch if specified."""

    try:
        verify_ollama_setup()
    except RuntimeError as e:
        click.echo(f"Error: {e}")
        return

    repo = get_repo()
    if not repo:
        click.echo("Not a valid Git repository.")
        return

    try:
        changes = get_diff(repo, branch, staged)
    except GitIntegrationError as error:
        click.echo(f"Failed to analyse Git changes: {error}")
        return

    if not changes:
        click.echo("No changes detected.")
        return

    suggestions = execute_with_spinner(get_local_llm_code_suggestions, KOALA_REVIEW_LOADING_MESSAGES, changes)

    format_output(suggestions)


@click.command()
@click.option("--model", type=str, help="Set the model to use (e.g., 'mistral-nemo:12b')")
@click.option("--show", is_flag=True, help="Show current configuration")
def config(model: Optional[str], show: bool) -> None:
    """Configure CodeKoala settings."""
    if model:
        set_config("model", model)
        click.echo(f"Model set to: {model}")

    if show:
        click.echo("Current Configuration:")
        for key, value in load_config().items():
            click.echo(f"  {key}: {value}")


@click.command()
@click.option(
    "-p", "--prompt-only",
    is_flag=True,
    help=(
        "Only generate the commit message prompt and copy it to your clipboard, "
        "ready to be pasted into an online LLM of your choosing."
    ),
)
@click.option(
    "-c", "--context",
    type=str,
    multiple=True,
    help="Additional context for the AI. Pass multiple times to add more.",
)
@click.option(
    "-f", "--context-file",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=str),
    multiple=True,
    help="Path to a file to include as additional context. Repeat to add more.",
)
@click.option(
    "-t", "--ticket",
    type=str,
    help="Ticket number to enforce in the generated commit message.",
)
def generate_message(prompt_only, context, context_file, ticket):
    """Generate an LLM-powered commit message."""
    console = Console()
    try:
        repo = Repo('.')
        changes = get_diff(repo, None, True)

        if not changes:
            console.print("[yellow]No changes detected[/yellow]")
            return

        user_context_parts = []

        if context:
            user_context_parts.append("\n".join(context).strip())

        for file_path in context_file:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                user_context_parts.append(file_handle.read().strip())

        user_context = "\n\n".join(part for part in user_context_parts if part).strip() or None
        user_ticket = ticket.strip() if ticket else None

        if prompt_only:
            prompt = COMMIT_MESSAGE_SYSTEM_PROMPT
            prompt += prepare_llm_commit_message_prompt(changes, user_context=user_context, user_ticket=user_ticket)
            pyperclip.copy(prompt)
            console.print(
                "[green]Commit message prompt copied to clipboard! Paste it into your preferred LLM interface.[/green]"
            )
            console.print()  # print a blank line
            console.print(
                "[yellow]⚠️ Warning: Pasting this content into an online model may expose your code to third parties. "
                "Ensure you're comfortable sharing your code before proceeding.[/yellow]"
            )
        else:
            message = execute_with_spinner(
                get_local_llm_commit_message,
                KOALA_COMMIT_LOADING_MESSAGES,
                changes,
                user_context=user_context,
                user_ticket=user_ticket,
            )
            console.print(message)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


cli.add_command(review_code)
cli.add_command(generate_message)
cli.add_command(config)

if __name__ == "__main__":
    cli()
