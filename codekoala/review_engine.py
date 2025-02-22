from ollama import chat
from ollama import ChatResponse

def analyze_code(diff):
    """Analyzes the diff and generates review suggestions (simplified)."""
    suggestions = []
    return suggestions

def get_local_llm_code_suggestions(code_diff: str) -> str:
    """Fetch code suggestions from the locally running CodeLlama model."""
    if not code_diff:
        return
    
    response: ChatResponse = chat(model="codellama", messages=[
        {
            "role": "system",
            "content": """
                You are a code review assistant. Below, you will find a Git diff of a code change. Please review the code changes and provide suggestions for improvement. Focus on the following aspects:
                    - Best programming practices
                    - SOLID principles
                    - Design patterns
                    - Code readability and maintainability
                    - Efficiency and performance improvements
                    - Avoiding common code smells

                If the code is already well-structured and adheres to good practices, kindly mention that as well.
            """
        },
        {"role": "user", "content": "Here is a Git diff of some code changes. Please review them."},
        {"role": "user", "content": "{code_diff}"},
        {"role": "assistant", "content": "Your suggestions: [Suggestions Here]"}
    ])


    return response.message.content