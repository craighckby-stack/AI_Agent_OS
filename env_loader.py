"""
==============================================================================
ARCHITECTURAL SYSTEM HEADER: ENVIRONMENT LOADER & CONFIGURATION CONTROLLER
==============================================================================
Role: Environment Configuration & Variable Expansion Engine
Diagnostic Integrity Hook: Enabled (via env_diagnostic_utils.py)
System Context: This module serves as the foundational bootstrap layer of the
                Local Agent Kernel. It executes before any other system component
                to guarantee that all API keys, model endpoints, and operational
                parameters are correctly loaded, validated, and expanded.
Integrations:
  - kernel.py: Bootstraps the kernel environment.
  - llm_router.py: Provides API keys and local model URLs.
  - env_validator.py: Performs schema integrity checks.
  - env_diagnostic_utils.py: Provides runtime health verification.
  - .env / .env.example: Reads and parses configuration schemas.
==============================================================================
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from env_validator import verify_env_integrity
from env_diagnostic_utils import log_diagnostic_event, perform_env_integrity_check

ENV_FILE = Path(__file__).parent / ".env"


def parse_env_text(text: str) -> Dict[str, str]:
    """
    Parses the raw content of a .env file into a dictionary of key-value pairs.
    Handles: single/double quotes, inline comments, and multi-line values.
    """
    env_dict: Dict[str, str] = {}
    lines = text.splitlines()
    
    current_key: Optional[str] = None
    current_value_lines: List[str] = []
    in_quote: Optional[str] = None
    
    for line in lines:
        stripped = line.strip()
        if in_quote is None:
            if not stripped or stripped.startswith("#"): continue
            if "=" not in line: continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip()
            if val.startswith('"') and not (val.endswith('"') and len(val) >= 2 and val[-2] != '\'):
                in_quote, current_key = '"', key
                current_value_lines.append(val[1:])
            elif val.startswith("'") and not (val.endswith("'") and len(val) >= 2 and val[-2] != '\'):
                in_quote, current_key = "'", key
                current_value_lines.append(val[1:])
            else:
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                else:
                    val, _, _ = val.partition("#")
                    val = val.strip()
                env_dict[key] = val.replace('\"', '"').replace("\'", "'")
        else:
            if stripped.endswith(in_quote) and not (stripped.endswith('\\' + in_quote) and len(stripped) >= 2):
                current_value_lines.append(line[:line.rfind(in_quote)])
                if current_key:
                    env_dict[current_key] = "\n".join(current_value_lines).replace('\"', '"').replace("\'", "'")
                in_quote, current_key, current_value_lines = None, None, []
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

    for key, val in env_dict.items():
        current_val = val
        for _ in range(5):
            if '$' not in current_val: break
            current_val = var_pattern.sub(replace_match, current_val)
        expanded[key] = current_val
    return expanded


def load_env() -> None:
    """
    Loads environment variables from the .env file. 
    Triggers post-load integrity verification and diagnostic logging.
    """
    if not ENV_FILE.exists(): 
        log_diagnostic_event("ENV_LOADER", "MISSING_FILE", "No .env file found.")
        return
    try:
        raw_text = ENV_FILE.read_text(encoding="utf-8")
        parsed = parse_env_text(raw_text)
        expanded = expand_variables(parsed)
        for key, value in expanded.items():
            os.environ.setdefault(key, value)
        
        # Post-load integrity check
        verify_env_integrity()
        perform_env_integrity_check()
        log_diagnostic_event("ENV_LOADER", "SUCCESS", "Environment loaded and verified.")
    except Exception as e:
        log_diagnostic_event("ENV_LOADER", "FAILURE", str(e))
        print(f"[env_loader warning] Failed to load .env file: {e}")


def get_env(key: str, default: Optional[str] = None) -> Optional[str]: return os.environ.get(key, default)
def get_bool(key: str, default: bool = False) -> bool: return os.environ.get(key, "").lower() in ("true", "1", "yes", "on") if key in os.environ else default
def get_int(key: str, default: int = 0) -> int:
    try: return int(os.environ.get(key, default))
    except: return default
def get_list(key: str, default: Optional[List[str]] = None, separator: str = ",") -> List[str]:
    val = os.environ.get(key)
    return [item.strip() for item in val.split(separator) if item.strip()] if val else (default or [])