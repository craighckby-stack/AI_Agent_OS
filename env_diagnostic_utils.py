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

# Configure diagnostic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DiagnosticEngine")

def log_diagnostic_event(source: str, status: str, message: str) -> None:
    """Logs diagnostic events to the system stream."""
    logger.info(f"[{source}] {status}: {message}")

def perform_env_integrity_check() -> Dict[str, Any]:
    """
    Performs a deep integrity check on loaded environment variables.
    Delegates schema validation to the env_validator module.
    """
    try:
        is_valid, details = validate_env_schema()
        report = {
            "status": "HEALTHY" if is_valid else "CRITICAL_FAILURE",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "details": details
        }
        
        if not is_valid:
            logger.warning(f"[DIAGNOSTIC] Environment health degraded: {details}")
            
        return report
    except Exception as e:
        logger.error(f"[DIAGNOSTIC] Fatal error during env diagnostic: {e}")
        return {
            "status": "ERROR",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "error": str(e)
        }