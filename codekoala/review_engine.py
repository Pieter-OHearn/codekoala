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
        {"role": "user", "content": f"{prepare_llm_review_prompt(changes)}"},
    ])

    return response.message.content

def get_local_llm_commit_message(changes: List[FileChange]) -> str:
    """Generates a commit message using a locally running LLM."""
    if not changes:
        return
    response: ChatResponse = chat(model=get_config_value("model"), messages=[
        {
            "role": "system",
            "content": """
                You are a git commit message generator that follows the Conventional Commits standard (https://www.conventionalcommits.org/).

                Given the following git changes, generate a single commit message following this format:
                <type>[optional scope]: <description>

                [optional body]

                [optional footer(s)]

                Rules:
                - Type must be one of: feat, fix, docs, style, refactor, perf, test, build, ci, chore
                - Description should be in imperative mood, lowercase, no period
                - Keep first line under 72 characters
                - Provide only the commit message with no other text
                - Break BREAKING CHANGE commits with an exclamation mark after the type/scope
                - If multiple changes, focus on the primary change
            """
        },
        {"role": "user", "content": f"{prepare_llm_commit_message_prompt(changes)}"},
    ])
    
    return response.message.content

def prepare_llm_review_prompt(changes: List[FileChange]) -> str:
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
    prompt = "Review these git changes and generate a commit message:"
    
    for change in changes:
        prompt += f"File: {change.path}\n"
        prompt += f"Change Type: {change.change_type}\n"
        prompt += f"Diff:\n{change.content}\n"
        prompt += "-" * 50 + "\n"
    return prompt