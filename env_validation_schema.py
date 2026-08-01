"""
ARCHITECTURAL SCHEMA: ENV VALIDATION GATEKEEPER
Role: Defines and enforces strict validation rules for environment configuration.
Integration: Acts as the primary integrity layer for env_loader.py and diagnostic_engine.py.

This schema implements a manifest-driven validation strategy siphoned from high-scale 
enterprise architectures, ensuring that the kernel only initializes with a 
mathematically and logically sound configuration state.
"""

from __future__ import annotations
import datetime
from typing import List, Dict, Any, NamedTuple, Optional

# Delegation: Import complex logic and telemetry from dedicated utilities
from src.utils.validation_logic import ValidationLogic
from src.utils.schema_telemetry import SchemaTelemetry

# --- DIAGNOSTIC INTEGRITY METADATA ---
SYSTEM_HEALTH_VERSION = "1.1.0"
PROTOCOL_VERSION = "DIAGNOSTIC_V2_MANIFEST"

class ValidationResult(NamedTuple):
    passed: bool
    message: str
    metadata: Dict[str, Any]
    severity: str = "CRITICAL"  # CRITICAL, WARNING, INFO
    remediation: Optional[str] = None

# --- ARCHITECTURAL MANIFEST ---
# Defines the source of truth for all environment variables
ENV_SCHEMA_MANIFEST = {
    "GEMINI_API_KEY": {"type": "str", "required": True, "description": "Primary LLM API Key"},
    "OPENAI_API_KEY": {"type": "str", "required": True, "description": "Fallback LLM API Key"},
    "SYSTEM_MODE": {
        "type": "enum", 
        "options": ["PRODUCTION", "DEVELOPMENT", "TEST"], 
        "default": "DEVELOPMENT"
    },
    "DIAGNOSTIC_LOG_LEVEL": {
        "type": "enum",
        "options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "default": "INFO"
    },
    "MEMORY_PRUNING_STRATEGY": {
        "type": "enum",
        "options": ["ENTROPY", "LRU", "FIFO"],
        "default": "ENTROPY"
    },
    "LLM_FALLBACK_STRATEGY": {
        "type": "enum",
        "options": ["STRICT", "GRACEFUL", "NONE"],
        "default": "GRACEFUL"
    },
    "MEMORY_LOCK_TIMEOUT": {"type": "int", "min": 100, "max": 10000, "default": 5000}
}

VERIFICATION_REGISTRY = {
    "schema_version": SYSTEM_HEALTH_VERSION,
    "protocol": PROTOCOL_VERSION,
    "last_updated": datetime.datetime.utcnow().isoformat() + "Z",
    "manifest_keys": list(ENV_SCHEMA_MANIFEST.keys())
}

class SchemaValidator:
    """Encapsulates manifest-driven validation logic with integrated telemetry."""
    
    @staticmethod
    def get_required_keys() -> List[str]:
        """Returns keys marked as required in the manifest."""
        return [k for k, v in ENV_SCHEMA_MANIFEST.items() if v.get("required", False)]

    @staticmethod
    def validate_key_format(key: str, value: Any) -> ValidationResult:
        """
        Validates a specific key against the manifest rules.
        Delegates complex logic to ValidationLogic utility.
        """
        if key not in ENV_SCHEMA_MANIFEST:
            return ValidationResult(
                passed=True, 
                message=f"Key {key} not in manifest, skipping strict validation.",
                metadata={"key": key},
                severity="INFO"
            )

        spec = ENV_SCHEMA_MANIFEST[key]
        return ValidationLogic.execute_spec_validation(key, value, spec)

    @classmethod
    def validate_full_environment(cls, env_data: Dict[str, Any]) -> Dict[str, ValidationResult]:
        """
        Performs a full suite validation with telemetry.
        Siphoned from AI_Agent_OS diagnostic_engine.py patterns.
        """
        results = {}
        with SchemaTelemetry.track_validation_cycle() as telemetry:
            for key, spec in ENV_SCHEMA_MANIFEST.items():
                value = env_data.get(key)
                if value is None and spec.get("required", False):
                    results[key] = ValidationResult(
                        passed=False,
                        message=f"Missing required key: {key}",
                        metadata={"key": key},
                        remediation=f"Add {key} to your .env file."
                    )
                else:
                    # Use default if value is missing but not required
                    val_to_check = value if value is not None else spec.get("default")
                    results[key] = cls.validate_key_format(key, val_to_check)
            
            telemetry.record_results(results)
        return results

    @staticmethod
    def get_registry_status() -> Dict[str, Any]:
        """Update timestamp on access to ensure diagnostic freshness."""
        VERIFICATION_REGISTRY["last_updated"] = datetime.datetime.utcnow().isoformat() + "Z"
        return VERIFICATION_REGISTRY

# --- LEGACY WRAPPERS FOR KERNEL COMPATIBILITY ---

def get_required_keys() -> List[str]:
    """Legacy hook for env_loader.py"""
    return SchemaValidator.get_required_keys()

def validate_key_format(key: str, value: str) -> bool:
    """Legacy hook for diagnostic_engine.py"""
    return SchemaValidator.validate_key_format(key, value).passed