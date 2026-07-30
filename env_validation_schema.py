"""
ARCHITECTURAL SCHEMA: ENV VALIDATION
Role: Defines validation rules for environment variables.
"""
from typing import List

REQUIRED_KEYS = ["GEMINI_API_KEY", "OPENAI_API_KEY", "SYSTEM_MODE"]

def get_required_keys() -> List[str]:
    return REQUIRED_KEYS

def validate_key_format(key: str, value: str) -> bool:
    """Validates specific format requirements for environment keys."""
    if key == "SYSTEM_MODE":
        return value in ["PRODUCTION", "DEVELOPMENT", "TEST"]
    return len(value) > 0