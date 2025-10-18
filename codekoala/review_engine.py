import json
import re
from typing import Any, Dict, List, Optional
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

def get_local_llm_commit_message(
    changes: List[FileChange],
    user_context: Optional[str] = None,
    user_ticket: Optional[str] = None,
) -> str:
    """Generates a commit message using a locally running LLM."""
    if not changes:
        return ""

    user_prompt = prepare_llm_commit_message_prompt(
        changes,
        user_context=user_context,
        user_ticket=user_ticket,
    )
    response: ChatResponse = chat(model=get_config_value("model"), messages=[
        {"role": "system", "content": COMMIT_MESSAGE_SYSTEM_PROMPT},
        {"role": "user", "content": f"{user_prompt}"},
    ])

    return _format_llm_commit_message_response(
        response.message.content,
        user_ticket=user_ticket,
    )

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

def prepare_llm_commit_message_prompt(
    changes: List[FileChange],
    user_context: Optional[str] = None,
    user_ticket: Optional[str] = None,
) -> str:
    """Create prompt for LLM commit message generation."""
    prompt_sections = ["Generate a commit message for the following changes."]

    if user_context:
        prompt_sections.append("Additional project context provided by the user:")
        prompt_sections.append(user_context)
        prompt_sections.append("-" * 50)

    normalized_ticket = _normalize_ticket(user_ticket)
    if normalized_ticket:
        prompt_sections.append("Ticket number provided by the user (must be used exactly):")
        prompt_sections.append(normalized_ticket)
        prompt_sections.append("-" * 50)

    for change in changes:
        prompt_sections.append(f"File: {change.path}")
        prompt_sections.append(f"Change Type: {change.change_type}")
        prompt_sections.append("Diff:")
        prompt_sections.append(_get_changed_section(change.content))
        prompt_sections.append("-" * 50)

    return "\n".join(prompt_sections)

def _get_changed_section(diff_content: str) -> str:
    """Extract only the changed lines from the diff content."""
    lines = diff_content.splitlines()
    changed_lines = []
    for line in lines:
        if line.startswith('+') or line.startswith('-'):
            changed_lines.append(line)
    return "\n".join(changed_lines)

COMMIT_MESSAGE_SYSTEM_PROMPT = """
You are an assistant that writes git commit messages for a development team. The team uses the following strict templates:

- {type}(#ticket): {imperative description}
- {type}: {imperative description} (when no ticket applies)

Optional bullet points for rationale follow, each prefixed with "- ".

Rules you must follow:
- Allowed type values: chore, feature, bugfix, hotfix.
- Use the ticket supplied in the prompt when one is provided.
- If no ticket is provided or applicable, omit the ticket entirely.
- The description must be short, in the imperative mood, and must not end with a period.
- Return context-aware bullets only when they add meaningful rationale or implementation details.
- Keep bullet text concise; each bullet should be a single sentence fragment.

Respond ONLY with a single JSON object (no code fences, no additional text) that matches this schema:

{
  "type": "chore|feature|bugfix|hotfix",
  "ticket": "#12345 or null",
  "description": "imperative summary without trailing period",
  "extras": ["optional bullet point", "..."]
}

If you have no bullets, respond with `"extras": []`.
"""

ALLOWED_COMMIT_TYPES = {"chore", "feature", "bugfix", "hotfix"}

_JSON_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _format_llm_commit_message_response(raw_response: str, user_ticket: Optional[str] = None) -> str:
    payload = _parse_commit_message_payload(raw_response)
    commit_type = str(payload.get("type", "")).lower().strip()
    ticket = payload.get("ticket", "")
    description = str(payload.get("description", "")).strip()
    extras = payload.get("extras", [])

    if commit_type not in ALLOWED_COMMIT_TYPES:
        commit_type = "chore"

    if user_ticket:
        normalized_ticket = _normalize_ticket(user_ticket)
    else:
        normalized_ticket = ""

    if not description:
        description = "update code"

    if normalized_ticket:
        formatted_lines = [f"{commit_type}({normalized_ticket}): {description}"]
    else:
        formatted_lines = [f"{commit_type}: {description}"]

    normalized_extras = []
    if isinstance(extras, list):
        normalized_extras = [
            cleaned for cleaned in (_normalize_bullet(str(item)) for item in extras)
            if cleaned
        ]
    elif extras:
        cleaned = _normalize_bullet(str(extras))
        if cleaned:
            normalized_extras = [cleaned]

    if normalized_extras:
        formatted_lines.append("")
        formatted_lines.extend(f"- {item}" for item in normalized_extras)

    return "\n".join(formatted_lines)


def _parse_commit_message_payload(raw_response: str) -> Dict[str, Any]:
    candidates = []
    content = raw_response.strip()

    for match in _JSON_BLOCK_PATTERN.finditer(content):
        candidates.append(match.group(1).strip())

    if content:
        candidates.append(content)

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload

    return {
        "type": "chore",
        "ticket": None,
        "description": "update code",
        "extras": ["Failed to parse commit message response.", content],
    }


def _normalize_ticket(ticket: Optional[Any]) -> str:
    if ticket is None:
        return ""
    ticket_str = str(ticket).strip()
    if not ticket_str:
        return ""
    if not ticket_str.startswith("#"):
        ticket_str = f"#{ticket_str}"
    return ticket_str


def _normalize_bullet(item: str) -> str:
    cleaned = re.sub(r"^\s*[-•*]+\s*", "", item).strip()
    return cleaned
