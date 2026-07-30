"""
ARCHITECTURAL SCHEMA VALIDATOR
Role: Provides granular validation logic for environment configurations.
Integration: Connects to diagnostic_engine.py for system health verification.

This module acts as a verifiable component of the system's health monitoring suite.
"""

import datetime
from typing import Dict, List, Any
from lib.env_schema_definitions import SCHEMA_RULES

# SYSTEM HEALTH CONSTANTS
SYSTEM_HEALTH_VERSION = "1.0.0"
PROTOCOL_VERSION = "DIAGNOSTIC_V1"

class SchemaValidator:
    """Encapsulates environment validation logic with lifecycle tracking."""
    
    def __init__(self):
        self.verification_registry = {
            "version": SYSTEM_HEALTH_VERSION,
            "protocol": PROTOCOL_VERSION,
            "last_check": datetime.datetime.utcnow().isoformat() + "Z"
        }

    def validate_schema(self, env: Dict[str, Any]) -> List[str]:
        """
        Performs deep validation on environment variable formats based on registered rules.
        """
        errors = []
        self.verification_registry["last_check"] = datetime.datetime.utcnow().isoformat() + "Z"

        for key, rule in SCHEMA_RULES.items():
            value = env.get(key)
            if value and value not in rule.get("allowed", []):
                errors.append(f"Invalid {key}: {value}. Expected one of: {rule.get('allowed')}")
        
        return errors

    def get_integrity_report(self) -> Dict[str, Any]:
        """Returns the current state of the validator for the diagnostic engine."""
        return self.verification_registry

# Global instance for system-wide access
validator = SchemaValidator()

def validate_schema(env: Dict[str, Any]) -> List[str]:
    """Legacy wrapper for SchemaValidator.validate_schema."""
    return validator.validate_schema(env)