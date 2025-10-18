import subprocess
from typing import Tuple


from codekoala.config import get_config_value

def verify_ollama_setup() -> None:
    """
    Verify Ollama setup and raise informative errors if not properly configured.
    """
    is_available, message = _check_ollama_availability()
    if not is_available:
        raise RuntimeError(f"Ollama setup incomplete: {message}")

def _check_ollama_availability() -> Tuple[bool, str]:
    """
    Check if Ollama is installed and running.
    Returns (is_available, message)
    """
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if get_config_value("model") in result.stdout:
            return True, "Ollama is installed and required model is available."
        return False, "Ollama is installed but the configured model is missing. Install it with 'ollama pull mistral-nemo:12b'"
    except FileNotFoundError:
        return False, "Ollama is not installed. Please install it from https://ollama.ai"
