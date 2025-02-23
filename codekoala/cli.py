import click
from typing import Optional
from rich.console import Console
from git import Repo
import pyperclip

from codekoala.koala_messages import KOALA_COMMIT_LOADING_MESSAGES, KOALA_REVIEW_LOADING_MESSAGES
from codekoala.verify_ollama import verify_ollama_setup
from codekoala.git_integration import get_repo, get_diff
from codekoala.review_engine import COMMIT_MESSAGE_SYSTEM_PROMPT, get_local_llm_code_suggestions, get_local_llm_commit_message, prepare_llm_commit_message_prompt
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

    changes = get_diff(repo, branch, staged)

    if not changes:
        click.echo("No changes detected.")
        return

    suggestions = execute_with_spinner(get_local_llm_code_suggestions, KOALA_REVIEW_LOADING_MESSAGES, changes)

    format_output(suggestions)

@click.command()
@click.option("--model", type=str, help="Set the model to use (e.g., 'codellama')")
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
@click.option('--prompt-only', is_flag=True, help="Only generate the commit message prompt and copy it to your clipboard, ready to be pasted into an online LLM of your choosing.")
def generate_message(prompt_only):
    """Generate an LLM-powered commit message."""
    console = Console()
    try:
        repo = Repo('.')
        changes = get_diff(repo, None, True)
        
        if not changes:
            console.print("[yellow]No changes detected[/yellow]")
            return

        if prompt_only:
            prompt = COMMIT_MESSAGE_SYSTEM_PROMPT
            prompt += prepare_llm_commit_message_prompt(changes)
            pyperclip.copy(prompt)
            console.print("[green]Commit message prompt copied to clipboard! Paste it into your preferred LLM interface.[/green]")
            console.print() # print a blank line
            console.print("[yellow]⚠️ Warning: Pasting this content into an online model may expose your code to third parties. Ensure you're comfortable sharing your code before proceeding.[/yellow]")
        else:
            message = execute_with_spinner(get_local_llm_commit_message, KOALA_COMMIT_LOADING_MESSAGES, changes)
            console.print(message)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

cli.add_command(review_code)
cli.add_command(generate_message)
cli.add_command(config)

if __name__ == "__main__":
    cli()