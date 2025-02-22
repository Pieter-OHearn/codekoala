import click
from git_integration import get_repo, get_diff
from review_engine import get_local_llm_code_suggestions
from formatter import format_output
from typing import Optional

@click.command()
@click.option("--branch", default=None, help="Branch to compare against")
@click.option("--staged", is_flag=True, help="Only review staged changes")
def review_code(branch: Optional[str], staged: bool) -> None:
    """Reviews code changes before committing, comparing with a branch if specified."""
    
    repo = get_repo()
    if not repo:
        print("Not a valid Git repository.")
        return

    diff = get_diff(repo, branch, staged)

    if not diff:
        print("No changes detected.")
        return

    suggestions = get_local_llm_code_suggestions(diff)

    format_output(diff, suggestions)

if __name__ == "__main__":
    review_code()
