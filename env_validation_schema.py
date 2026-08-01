"""
ARCHITECTURAL SCHEMA: ENV VALIDATION
Role: Defines validation rules for environment variables.
Integration: Connects to diagnostic_engine.py for real-time system health monitoring.

This schema acts as the primary gatekeeper for environment integrity, ensuring all 
critical configuration keys are verified before kernel execution cycles.
"""

from typing import List, Dict, Any, NamedTuple
import datetime

# --- DIAGNOSTIC INTEGRITY HOOK ---
SYSTEM_HEALTH_VERSION = "1.0.0"
PROTOCOL_VERSION = "DIAGNOSTIC_V1"

class ValidationResult(NamedTuple):
    passed: bool
    message: str
    metadata: Dict[str, Any]

VERIFICATION_REGISTRY = {
    "schema_version": SYSTEM_HEALTH_VERSION,
    "protocol": PROTOCOL_VERSION,
    "last_updated": datetime.datetime.utcnow().isoformat() + "Z"
}

REQUIRED_KEYS = ["GEMINI_API_KEY", "OPENAI_API_KEY", "SYSTEM_MODE"]

class SchemaValidator:
    """Encapsulates validation logic for environment configuration with diagnostic telemetry."""
    
    @staticmethod
    def get_required_keys() -> List[str]:
        return REQUIRED_KEYS

    @staticmethod
    def validate_key_format(key: str, value: str) -> ValidationResult:
        """Validates specific format requirements and returns a structured diagnostic result."""
        if key == "SYSTEM_MODE":
            is_valid = value in ["PRODUCTION", "DEVELOPMENT", "TEST"]
            return ValidationResult(
                passed=is_valid,
                message="Valid SYSTEM_MODE" if is_valid else f"Invalid mode: {value}",
                metadata={"key": key, "value": value}
            )
        
        is_valid = isinstance(value, str) and len(value) > 0
        return ValidationResult(
            passed=is_valid,
            message=f"Key {key} is valid" if is_valid else f"Key {key} is empty or invalid",
            metadata={"key": key}
        )

    @staticmethod
    def get_registry_status() -> Dict[str, Any]:
        # Update timestamp on access to ensure diagnostic freshness
        VERIFICATION_REGISTRY["last_updated"] = datetime.datetime.utcnow().isoformat() + "Z"
        return VERIFICATION_REGISTRY

def get_required_keys() -> List[str]:
    return SchemaValidator.get_required_keys()

def validate_key_format(key: str, value: str) -> bool:
    """Legacy wrapper for compatibility with existing diagnostic hooks."""
    return SchemaValidator.validate_key_format(key, value).passed