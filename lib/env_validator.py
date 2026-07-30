"""
ENVIRONMENT SCHEMA VALIDATOR
Role: Validates the integrity of loaded environment variables against required schemas.
Integration: Called by kernel.py and diagnostic-engine.py for system health verification.

This module serves as a critical gatekeeper for environment configuration, ensuring
that all required system variables are present and valid before kernel initialization.
"""

import os
import logging
from typing import Tuple, Dict, Any
from lib.env_schema_definitions import REQUIRED_ENV_KEYS

# System Integrity Constants
SYSTEM_HEALTH_VERSION = "1.0.0"
PROTOCOL_VERSION = "DIAGNOSTIC_V1"

# Diagnostic Registry Hook
VERIFICATION_REGISTRY = {
    "validator_type": "EnvValidator",
    "version": SYSTEM_HEALTH_VERSION,
    "protocol": PROTOCOL_VERSION
}

logger = logging.getLogger("EnvValidator")

class EnvValidator:
    """
    Encapsulates environment validation logic with stateful tracking.
    """
    def __init__(self, required_keys: list = None):
        self.required_keys = required_keys or REQUIRED_ENV_KEYS
        self.registry = VERIFICATION_REGISTRY

    def validate(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Performs schema-based validation of environment variables.
        Returns (is_valid, details).
        """
        try:
            missing = [key for key in self.required_keys if key not in os.environ]
            is_valid = len(missing) == 0
            
            details = {
                "missing_keys": missing,
                "total_checked": len(self.required_keys),
                "status": "VALID" if is_valid else "INVALID",
                "version": self.registry["version"]
            }
            
            if not is_valid:
                logger.warning(f"[ENV_VALIDATOR] Validation failed: Missing {missing}")
                
            return is_valid, details
        except Exception as e:
            logger.error(f"[ENV_VALIDATOR] Critical error during validation: {e}")
            return False, {"error": str(e)}

def validate_env_schema() -> Tuple[bool, Dict[str, Any]]:
    """
    Legacy-compatible wrapper for the EnvValidator class.
    """
    validator = EnvValidator()
    return validator.validate()