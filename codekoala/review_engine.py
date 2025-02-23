from typing import List
from ollama import chat, ChatResponse

from codekoala.config import get_config_value
from codekoala.git_integration import FileChange

def get_local_llm_code_suggestions(changes: List[FileChange]) -> str:
    """Fetch code suggestions from the locally running CodeLlama model."""
    if not changes:
        return
    response: ChatResponse = chat(model=get_config_value("model"), messages=[
        {
            "role": "system",
            "content": """
                You are a code review assistant. Below is a Git diff of some code changes. Review the code and provide structured feedback, ensuring your response adheres to the following format **exactly**:

                **Evaluation Criteria:**
                    - Best programming practices
                    - SOLID principles
                    - Design patterns
                    - Code readability and maintainability
                    - Efficiency and performance improvements
                    - Identifying and avoiding common code smells

                **Output Format (strictly follow this structure):**

                [bold yellow]Issues/Bugs:[/bold yellow]
                - <Issue 1 description>
                - <Issue 2 description>

                [bold cyan]Recommended Refactors:[/bold cyan]
                - <Refactor 1 description>
                - <Refactor 2 description>

                [bold green]Non-Essential Enhancements:[/bold green]
                - <Enhancement 1 description>
                - <Enhancement 2 description>

                **Important:**
                - If no issues are found, explicitly state: `[bold green]No issues found in this diff.[/bold green]`
                - Ensure the response includes all three sections, even if empty (e.g., "No recommended refactors for this diff").
                - Keep responses **concise yet informative**. Provide clear reasoning when suggesting improvements.

                **Example Response:**
                
                [bold yellow]Issues/Bugs:[/bold yellow]
                - Null reference exception risk in `UserService.getUserById` when `user` is None.

                [bold cyan]Recommended Refactors:[/bold cyan]
                - Extract the database query logic into a separate repository class for better separation of concerns.

                [bold green]Non-Essential Enhancements:[/bold green]
                - Rename `tempVar` to `userCount` for improved readability.
            """
        },
        {"role": "user", "content": f"{_prepare_llm_review_prompt(changes)}"},
    ])

    return response.message.content

def get_local_llm_commit_message(changes: List[FileChange]) -> str:
    """Generates a commit message using a locally running LLM."""
    if not changes:
        return
    response: ChatResponse = chat(model=get_config_value("model"), messages=[
        {"role": "system", "content": COMMIT_MESSAGE_SYSTEM_PROMPT},
        {"role": "user", "content": f"{prepare_llm_commit_message_prompt(changes)}"},
    ])
    
    return response.message.content

def _prepare_llm_review_prompt(changes: List[FileChange]) -> str:
    """Create prompt for LLM review."""
    prompt = "Please analyse these changes and review them based on the criteria outlined above:\n\n"
    
    for change in changes:
        prompt += f"File: {change.path}\n"
        prompt += f"Change Type: {change.change_type}\n"
        prompt += f"Diff:\n{change.content}\n"
        if change.old_content:
            prompt += f"Previous Content:\n{change.old_content}\n"
        prompt += "-" * 50 + "\n"

    return prompt

def prepare_llm_commit_message_prompt(changes: List[FileChange]) -> str:
    """Create prompt for LLM review."""
    prompt = "Generate a commit message for the following changes:"
    
    for change in changes:
        prompt += f"File: {change.path}\n"
        prompt += f"Change Type: {change.change_type}\n"
        prompt += f"Diff:\n{_get_changed_section(change.content)}\n"
        prompt += "-" * 50 + "\n"
    return prompt

def _get_changed_section(diff_content: str) -> str:
    """Extract only the changed lines from the diff content."""
    lines = diff_content.splitlines()
    changed_lines = []
    for line in lines:
        if line.startswith('+') or line.startswith('-'):
            changed_lines.append(line)
    return "\n".join(changed_lines)

COMMIT_MESSAGE_SYSTEM_PROMPT = """
You are a git commit message generator that strictly follows the Conventional Commits 1.0.0 specification (https://www.conventionalcommits.org/).

For the following git changes, generate a single commit message in the following format:

<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

Please note the following rules:
- The commit message should be **exactly** in the format outlined above.
- Type must be one of: feat, fix, docs, style, refactor, perf, test, build, ci, chore.
- Description should be in the imperative mood, lowercase, and **no period** at the end.
- Keep the first line under **72 characters**.
- Provide **only** the commit message, with **no additional explanation or text**.
- For BREAKING CHANGE commits, append an exclamation mark (!) to the type/scope.
- If there are multiple changes, focus on the primary change and generate a single commit message.
- Do **not** include any git diff information or extra context other than what's given in the following changes.
"""
