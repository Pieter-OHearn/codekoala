import json
from pathlib import Path
from typing import Dict, Any

CONFIG_FILE = Path.home() / ".config" / "codekoala" / "config.json"

DEFAULT_CONFIG = {
    "model": "codellama",
    # TODO: Allow future support for API-based LLMs
    "provider": "ollama",
    "api_key": None,
}

def load_config() -> Dict[str, Any]:
    """Load configuration from file, falling back to defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def set_config(key: str, value: Any) -> None:
    """Update a configuration key and save it."""
    config = load_config()
    config[key] = value
    save_config(config)

def get_config_value(key: str) -> Any:
    """Retrieve a configuration value."""
    return load_config().get(key, DEFAULT_CONFIG.get(key))
