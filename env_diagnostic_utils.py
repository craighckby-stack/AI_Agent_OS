"""
ARCHITECTURAL DIAGNOSTIC UTILITIES
Role: Provides runtime health verification for the environment loader.
Integration: Called by env_loader.py to ensure configuration integrity.

This module acts as the primary gatekeeper for environment health, ensuring all 
configuration dependencies are verified before system execution cycles.
"""

import logging
import datetime
from typing import Dict, Any
from lib.env_validator import validate_env_schema
from .diagnostic_engine_utils import format_timestamp, execute_check_with_telemetry
from .diagnostic_utils_core import generate_telemetry_metadata

# Configure diagnostic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DiagnosticEngine")

def log_diagnostic_event(source: str, status: str, message: str) -> None:
    """Logs diagnostic events to the system stream."""
    logger.info(f"[{source}] {status}: {message}")

def perform_env_integrity_check() -> Dict[str, Any]:
    """
    Performs a deep integrity check on loaded environment variables.
    Delegates schema validation to the env_validator module with integrated telemetry.
    """
    try:
        # Execute validation with telemetry tracking
        passed, duration = execute_check_with_telemetry(validate_env_schema, "env_schema_validation")
        
        # Retrieve detailed validation results
        _, details = validate_env_schema()
        
        report = {
            "status": "HEALTHY" if passed else "CRITICAL_FAILURE",
            "timestamp": format_timestamp(),
            "duration_ms": duration,
            "details": details,
            "telemetry": generate_telemetry_metadata()
        }
        
        if not passed:
            logger.warning(f"[DIAGNOSTIC] Environment health degraded: {details}")
            
        return report
    except Exception as e:
        logger.error(f"[DIAGNOSTIC] Fatal error during env diagnostic: {e}")
        return {
            "status": "ERROR",
            "timestamp": format_timestamp(),
            "error": str(e)
        }