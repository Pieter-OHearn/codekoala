from ollama import chat, ChatResponse

from codekoala.config import get_config_value

def analyze_code(diff):
    """Analyzes the diff and generates review suggestions (simplified)."""
    suggestions = []
    return suggestions

def get_local_llm_code_suggestions(code_diff: str) -> str:
    """Fetch code suggestions from the locally running CodeLlama model."""
    if not code_diff:
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
        {
            "role": "user",
            "content": f"""
                I have made changes to the following code. Could you please review it based on the criteria outlined above?

                git diff output: {code_diff}
            """
        },
    ])

    return response.message.content