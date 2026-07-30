"""
==============================================================================
ARCHITECTURAL SYSTEM HEADER: ENVIRONMENT LOADER & CONFIGURATION CONTROLLER
==============================================================================
Role: Environment Configuration & Variable Expansion Engine
System Context: This module serves as the foundational bootstrap layer of the
                Local Agent Kernel. It executes before any other system component
                to guarantee that all API keys, model endpoints, and operational
                parameters are correctly loaded, validated, and expanded.
Integrations:
  - kernel.py: Bootstraps the kernel environment.
  - llm_router.py: Provides API keys (GEMINI_API_KEY, OPENAI_API_KEY, etc.)
                   and local model URLs (LOCAL_LLM_URL).
  - .env / .env.example: Reads and parses configuration schemas.
==============================================================================
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

ENV_FILE = Path(__file__).parent / ".env"


def parse_env_text(text: str) -> Dict[str, str]:
    """
    Parses the raw content of a .env file into a dictionary of key-value pairs.
    Handles:
    - Single/double quotes
    - Inline comments (outside quotes)
    - Multi-line values
    """
    env_dict: Dict[str, str] = {}
    lines = text.splitlines()
    
    current_key: Optional[str] = None
    current_value_lines: List[str] = []
    in_quote: Optional[str] = None  # Can be '"' or "'"
    
    for line in lines:
        stripped = line.strip()
        
        if in_quote is None:
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in line:
                continue
                
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip()
            
            # Check for multi-line quotes
            if val.startswith('"') and not (val.endswith('"') and len(val) >= 2 and val[-2] != '\'):
                in_quote = '"'
                current_key = key
                current_value_lines.append(val[1:])
            elif val.startswith("'") and not (val.endswith("'") and len(val) >= 2 and val[-2] != '\'):
                in_quote = "'"
                current_key = key
                current_value_lines.append(val[1:])
            else: 
                # Single line value
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                else:
                    # Strip inline comment if any (outside of quotes)
                    val, _, _ = val.partition("#")
                    val = val.strip()
                
                # Unescape common escape sequences
                val = val.replace('\"', '"').replace("\'", "'").replace("\n", "\n")
                env_dict[key] = val
        else:
            # Inside a multi-line quote
            if stripped.endswith(in_quote) and not (stripped.endswith('\' + in_quote) and len(stripped) >= 2):
                current_value_lines.append(line[:line.rfind(in_quote)])
                if current_key:
                    full_val = "\n".join(current_value_lines)
                    full_val = full_val.replace('\"', '"').replace("\'", "'").replace("\n", "\n")
                    env_dict[current_key] = full_val
                in_quote = None
                current_key = None
                current_value_lines = []
            else:
                current_value_lines.append(line)
                
    return env_dict


def expand_variables(env_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Expands variables in the format ${VAR} or $VAR using values from
    the parsed env_dict or the existing os.environ.
    """
    expanded: Dict[str, str] = {}
    var_pattern = re.compile(r'\$\{([A-Za-z0-9_]+)\}|\$([A-Za-z0-9_]+)')
    
    def replace_match(match: re.Match) -> str:
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name, expanded.get(var_name, env_dict.get(var_name, "")))

    # Iterative resolution up to 5 passes to handle nested variables safely
    for key, val in env_dict.items():
        current_val = val
        for _ in range(5):
            if '$' not in current_val:
                break
            current_val = var_pattern.sub(replace_match, current_val)
        expanded[key] = current_val
        
    return expanded


def load_env() -> None:
    """
    Loads environment variables from the .env file in the repo root.
    Real environment variables always win over the file.
    """
    if not ENV_FILE.exists():
        return
    try:
        raw_text = ENV_FILE.read_text(encoding="utf-8")
        parsed = parse_env_text(raw_text)
        expanded = expand_variables(parsed)
        for key, value in expanded.items():
            os.environ.setdefault(key, value)
    except Exception as e:
        # Fail-safe: log warning but do not crash the kernel
        print(f"[env_loader warning] Failed to load .env file: {e}")


# ==============================================================================
# TYPE-SAFE CONFIGURATION GETTERS
# ==============================================================================

def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve an environment variable, falling back to default."""
    return os.environ.get(key, default)


def get_bool(key: str, default: bool = False) -> bool:
    """Retrieve an environment variable cast to boolean."""
    val = os.environ.get(key)
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes", "on")


def get_int(key: str, default: int = 0) -> int:
    """Retrieve an environment variable cast to integer."""
    val = os.environ.get(key)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


def get_list(key: str, default: Optional[List[str]] = None, separator: str = ",") -> List[str]:
    """Retrieve an environment variable cast to a list of strings."""
    val = os.environ.get(key)
    if val is None:
        return default or []
    return [item.strip() for item in val.split(separator) if item.strip()]