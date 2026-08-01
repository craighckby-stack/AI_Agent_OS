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
from lib.diagnostic_utils_core import DiagnosticResult, generate_telemetry_metadata

# System Integrity Constants
SYSTEM_HEALTH_VERSION = "1.0.0"
PROTOCOL_VERSION = "DIAGNOSTIC_V1"

logger = logging.getLogger("EnvValidator")

class EnvValidator:
    """
    Encapsulates environment validation logic with stateful tracking and telemetry.
    """
    def __init__(self, required_keys: list = None):
        self.required_keys = required_keys or REQUIRED_ENV_KEYS
        self.version = SYSTEM_HEALTH_VERSION

    def validate(self) -> DiagnosticResult:
        """
        Performs schema-based validation of environment variables.
        Returns a structured DiagnosticResult.
        """
        try:
            missing = [key for key in self.required_keys if key not in os.environ]
            is_valid = len(missing) == 0
            
            metadata = {
                "missing_keys": missing,
                "total_checked": len(self.required_keys),
                "telemetry": generate_telemetry_metadata(),
                "version": self.version
            }
            
            message = "Environment configuration valid" if is_valid else f"Missing keys: {', '.join(missing)}"
            
            if not is_valid:
                logger.warning(f"[ENV_VALIDATOR] Validation failed: {message}")
                
            return DiagnosticResult(passed=is_valid, message=message, metadata=metadata)
        except Exception as e:
            logger.error(f"[ENV_VALIDATOR] Critical error during validation: {e}")
            return DiagnosticResult(passed=False, message=str(e), metadata={"error": True})

def validate_env_schema() -> Tuple[bool, Dict[str, Any]]:
    """
    Legacy-compatible wrapper for the EnvValidator class.
    """
    validator = EnvValidator()
    result = validator.validate()
    return result.passed, {"status": "VALID" if result.passed else "INVALID", **result.metadata}