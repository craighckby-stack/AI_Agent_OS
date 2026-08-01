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
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Internal System Imports
from env_validator import verify_env_integrity
from env_diagnostic_utils import log_diagnostic_event, perform_env_integrity_check

# Siphoned Utility Delegations
from src.utils.env_telemetry import EnvTelemetry
from src.utils.env_expansion_engine import VariableExpander

# SYSTEM HEALTH CONSTANTS
SYSTEM_HEALTH_VERSION = "1.1.0-TELEMETRY-AWARE"
PROTOCOL_VERSION = "DIAGNOSTIC_V2"
ENV_FILE = Path(__file__).parent / ".env"

class DiagnosticRegistry:
    """Tracks the integrity state of the environment loader using a centralized registry pattern."""
    _registry = {
        "last_check": None, 
        "status": "INITIALIZED", 
        "version": SYSTEM_HEALTH_VERSION,
        "telemetry": {}
    }

    @classmethod
    def update_status(cls, status: str, telemetry: Optional[Dict[str, Any]] = None):
        cls._registry["status"] = status
        cls._registry["last_check"] = datetime.datetime.utcnow().isoformat() + "Z"
        if telemetry:
            cls._registry["telemetry"] = telemetry

    @classmethod
    def get_report(cls) -> Dict[str, Any]:
        return cls._registry

class EnvironmentState:
    """Container for managing environment state and preventing redundant mutations."""
    _cache: Dict[str, str] = {}

    @classmethod
    def update(cls, data: Dict[str, str]):
        cls._cache.update(data)

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        # Priority: Cache -> OS Environ -> Default
        return cls._cache.get(key, os.environ.get(key, default))

    @classmethod
    def clear(cls):
        cls._cache.clear()

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
            
            # Handle quoted values
            if val.startswith('"') and not (val.endswith('"') and len(val) >= 2 and val[-2] != '\\'):
                in_quote, current_key = '"', key
                current_value_lines.append(val[1:])
            elif val.startswith("'") and not (val.endswith("'") and len(val) >= 2 and val[-2] != '\\'):
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
            # Handle multi-line quoted values
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
    Delegates variable expansion to the RecursiveExpander engine.
    Supports ${VAR} and $VAR with cycle detection.
    """
    return VariableExpander.expand(env_dict, os.environ)

def load_env() -> None:
    """
    Loads environment variables from the .env file with integrated telemetry.
    Triggers post-load integrity verification and diagnostic logging.
    """
    telemetry = EnvTelemetry()
    
    def _execution_logic():
        if not ENV_FILE.exists(): 
            log_diagnostic_event("ENV_LOADER", "MISSING_FILE", "No .env file found.")
            DiagnosticRegistry.update_status("CRITICAL_FAILURE")
            return False

        raw_text = ENV_FILE.read_text(encoding="utf-8")
        parsed = parse_env_text(raw_text)
        expanded = expand_variables(parsed)
        
        EnvironmentState.update(expanded)
        for key, value in expanded.items():
            os.environ.setdefault(key, value)
        
        # Run integrity checks
        verify_env_integrity()
        perform_env_integrity_check()
        
        log_diagnostic_event("ENV_LOADER", "SUCCESS", "Environment loaded and verified.")
        DiagnosticRegistry.update_status("HEALTHY")
        return True

    try:
        success, duration = telemetry.measure_execution(_execution_logic)
        report = telemetry.generate_report(success, duration)
        DiagnosticRegistry.update_status("HEALTHY" if success else "ERROR", report)
    except Exception as e:
        log_diagnostic_event("ENV_LOADER", "FAILURE", str(e))
        DiagnosticRegistry.update_status("ERROR")
        print(f"[env_loader critical] Failed to load .env file: {e}")

def reload_env() -> None:
    """Force reloads the environment, clearing the internal state cache."""
    EnvironmentState.clear()
    load_env()

# --- Resilient Getters ---

def get_env(key: str, default: Optional[str] = None) -> Optional[str]: 
    return EnvironmentState.get(key, default)

def get_bool(key: str, default: bool = False) -> bool: 
    val = str(EnvironmentState.get(key, "")).lower()
    if not val and key not in os.environ: return default
    return val in ("true", "1", "yes", "on", "enabled")

def get_int(key: str, default: int = 0) -> int:
    try: 
        val = EnvironmentState.get(key)
        return int(val) if val is not None else default
    except (ValueError, TypeError): 
        return default

def get_list(key: str, default: Optional[List[str]] = None, separator: str = ",") -> List[str]:
    val = EnvironmentState.get(key)
    if val is None: return default or []
    return [item.strip() for item in val.split(separator) if item.strip()]