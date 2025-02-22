import subprocess
from typing import Tuple


from codekoala.config import get_config_value

def check_ollama_availability() -> Tuple[bool, str]:
    """
    Check if Ollama is installed and running.
    Returns (is_available, message)
    """
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if get_config_value("model") in result.stdout:
            return True, "Ollama is installed and CodeLlama model is installed"
        return False, "Ollama is installed but CodeLlama model is not installed. Install it with 'ollama pull codellama'"
    except FileNotFoundError:
        return False, "Ollama is not installed. Please install it from https://ollama.ai"

def verify_ollama_setup() -> None:
    """
    Verify Ollama setup and raise informative errors if not properly configured.
    """
    is_available, message = check_ollama_availability()
    if not is_available:
        raise RuntimeError(f"Ollama setup incomplete: {message}")