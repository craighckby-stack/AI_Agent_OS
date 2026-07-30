"""
ARCHITECTURAL DIAGNOSTIC UTILITIES
Role: Provides runtime health verification for the environment loader.
Integration: Called by env_loader.py to ensure configuration integrity.

This module acts as the primary gatekeeper for environment health, ensuring 
all critical configurations are verified before kernel execution cycles.
"""

import logging
from typing import Any, Dict
from env_validation_schema import validate_env_schema

# Configure diagnostic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DiagnosticEngine")

def log_diagnostic_event(source: str, status: str, message: str) -> None:
    """Logs diagnostic events to the system stream with structured formatting."""
    logger.info(f"[{source}] {status}: {message}")

def perform_env_integrity_check(env_data: Dict[str, Any]) -> bool:
    """
    Performs a deep integrity check on loaded environment variables.
    Delegates schema validation to the dedicated validation schema module.
    """
    try:
        log_diagnostic_event("EnvDiagnostic", "START", "Initiating environment integrity check...")
        
        is_valid = validate_env_schema(env_data)
        
        if is_valid:
            log_diagnostic_event("EnvDiagnostic", "SUCCESS", "Environment schema validation passed.")
        else:
            log_diagnostic_event("EnvDiagnostic", "FAILURE", "Environment schema validation failed.")
            
        return is_valid
    except Exception as e:
        logger.error(f"[EnvDiagnostic] Fatal error during integrity check: {e}")
        return False