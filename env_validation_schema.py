"""
ARCHITECTURAL SCHEMA: ENV VALIDATION
Role: Defines validation rules for environment variables.
Integration: Connects to diagnostic_engine.py for real-time system health monitoring.

This schema acts as the primary gatekeeper for environment integrity, ensuring all 
critical configuration keys are verified before kernel execution cycles.
"""

from typing import List, Dict, Any
import datetime

# --- DIAGNOSTIC INTEGRITY HOOK ---
SYSTEM_HEALTH_VERSION = "1.0.0"
PROTOCOL_VERSION = "DIAGNOSTIC_V1"

VERIFICATION_REGISTRY = {
    "schema_version": SYSTEM_HEALTH_VERSION,
    "protocol": PROTOCOL_VERSION,
    "last_updated": datetime.datetime.utcnow().isoformat() + "Z"
}

REQUIRED_KEYS = ["GEMINI_API_KEY", "OPENAI_API_KEY", "SYSTEM_MODE"]

class SchemaValidator:
    """Encapsulates validation logic for environment configuration."""
    
    @staticmethod
    def get_required_keys() -> List[str]:
        return REQUIRED_KEYS

    @staticmethod
    def validate_key_format(key: str, value: str) -> bool:
        """Validates specific format requirements for environment keys."""
        if key == "SYSTEM_MODE":
            return value in ["PRODUCTION", "DEVELOPMENT", "TEST"]
        return isinstance(value, str) and len(value) > 0

    @staticmethod
    def get_registry_status() -> Dict[str, Any]:
        return VERIFICATION_REGISTRY

def get_required_keys() -> List[str]:
    return SchemaValidator.get_required_keys()

def validate_key_format(key: str, value: str) -> bool:
    return SchemaValidator.validate_key_format(key, value)