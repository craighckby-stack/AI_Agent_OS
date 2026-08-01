"""
ENVIRONMENT SCHEMA TYPES
Role: Type definitions and TypedDict specifications for environment variable schemas and validation rules.
Integration: Imported by lib/env_schema_definitions.py and env_validator.py.
"""

from typing import List, Dict, Any, Optional, TypedDict

class EnvSchemaDefinition(TypedDict, total=False):
    required: List[str]
    optional: List[str]
    version: str
    strict_mode: bool
    allowed_environments: List[str]
    type_constraints: Dict[str, str]
