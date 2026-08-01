"""
ENVIRONMENT SCHEMA DEFINITIONS
Role: Centralized configuration for required environment variables and schema validation.
Integration: Used by env_validator.py to enforce system configuration integrity.
"""

from typing import List, Dict, Any
from lib.env_schema_types import EnvSchemaDefinition

# List of mandatory environment variables for system operation
REQUIRED_ENV_KEYS: List[str] = [
    "API_KEY",
    "DB_URL",
    "SYSTEM_ID",
    "ENVIRONMENT"
]

# Schema definition for runtime validation
ENV_SCHEMA: EnvSchemaDefinition = {
    "required": REQUIRED_ENV_KEYS,
    "version": "1.0.0",
    "strict_mode": True
}

def get_required_keys() -> List[str]:
    """Returns the list of mandatory environment keys."""
    return REQUIRED_ENV_KEYS

def validate_env_schema(env_vars: Dict[str, Any]) -> bool:
    """Validates that all required keys are present in the provided environment dictionary."""
    return all(key in env_vars for key in REQUIRED_ENV_KEYS)