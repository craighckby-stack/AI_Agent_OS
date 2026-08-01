"""
ENVIRONMENT SCHEMA DEFINITIONS & SYSTEM SPECIFICATION
Role: Centralized configuration and type schema definitions for environment variables and runtime validation rules.
Integration: Leveraged by env_validator.py and kernel execution context for runtime configuration verification and integrity checks.
"""

from typing import List, Dict, Any, Optional
from lib.env_schema_types import EnvSchemaDefinition

# List of mandatory environment variables for system operation
REQUIRED_ENV_KEYS: List[str] = [
    "API_KEY",
    "DB_URL",
    "SYSTEM_ID",
    "ENVIRONMENT"
]

# List of optional environment variables with default support
OPTIONAL_ENV_KEYS: List[str] = [
    "LOG_LEVEL",
    "DEBUG",
    "CACHE_TTL",
    "MAX_RETRIES"
]

# Schema definition for runtime validation
ENV_SCHEMA: EnvSchemaDefinition = {
    "required": REQUIRED_ENV_KEYS,
    "optional": OPTIONAL_ENV_KEYS,
    "version": "1.0.0",
    "strict_mode": True,
    "allowed_environments": ["development", "staging", "production", "test"],
    "type_constraints": {
        "API_KEY": "string",
        "DB_URL": "string",
        "SYSTEM_ID": "string",
        "ENVIRONMENT": "string",
        "LOG_LEVEL": "string",
        "DEBUG": "boolean",
        "CACHE_TTL": "integer",
        "MAX_RETRIES": "integer"
    }
}

def get_required_keys() -> List[str]:
    """Returns the list of mandatory environment keys."""
    return list(REQUIRED_ENV_KEYS)

def get_optional_keys() -> List[str]:
    """Returns the list of optional environment keys."""
    return list(OPTIONAL_ENV_KEYS)

def get_env_schema() -> EnvSchemaDefinition:
    """Returns a copy of the active environment validation schema."""
    return dict(ENV_SCHEMA)

def validate_env_schema(env_vars: Dict[str, Any]) -> bool:
    """Validates that all required keys are present in the provided environment dictionary."""
    if not isinstance(env_vars, dict):
        return False
    return all(key in env_vars and env_vars[key] is not None for key in REQUIRED_ENV_KEYS)

def validate_env_schema_detailed(env_vars: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs detailed validation against the environment schema, 
    returning missing keys, environment validity, and type check status.
    """
    if not isinstance(env_vars, dict):
        return {
            "valid": False,
            "missing_keys": list(REQUIRED_ENV_KEYS),
            "errors": ["Input environment must be a dictionary."]
        }

    missing_keys = [key for key in REQUIRED_ENV_KEYS if key not in env_vars or env_vars[key] is None]
    errors = []

    if missing_keys:
        errors.append(f"Missing required environment variables: {', '.join(missing_keys)}")

    env_val = env_vars.get("ENVIRONMENT")
    allowed_envs = ENV_SCHEMA.get("allowed_environments", [])
    if env_val and allowed_envs and env_val not in allowed_envs:
        errors.append(f"Invalid ENVIRONMENT '{env_val}'. Allowed values: {', '.join(allowed_envs)}")

    return {
        "valid": len(errors) == 0,
        "missing_keys": missing_keys,
        "errors": errors,
        "checked_keys": list(env_vars.keys())
    }
