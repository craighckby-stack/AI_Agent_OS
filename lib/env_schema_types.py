"""
ENVIRONMENT SCHEMA TYPES
Role: Type definitions for environment schema validation.
"""

from typing import TypedDict, List

class EnvSchemaDefinition(TypedDict):
    required: List[str]
    version: str
    strict_mode: bool