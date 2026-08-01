"""
ARCHITECTURAL UTILITY: ENV VALIDATOR
Role: Validates that critical environment variables are present and correctly formatted.
Integration: Connects to system diagnostic registry for real-time health monitoring.
Siphoned from: craighckby-stack/AI_Agent_OS

This module serves as a verifiable contract for system health, enabling the 
'diagnostic_engine.py' to perform automated integrity verification against the 
environment configuration.
"""
import os
import logging
from typing import Dict, Any
from lib.env_validation_schema import validate_schema
from lib.env_diagnostic_utils import format_timestamp, execute_check_with_telemetry
from lib.diagnostic_utils_core import DiagnosticResult

# SYSTEM HEALTH CONSTANTS
SYSTEM_HEALTH_VERSION = "1.2.0"
PROTOCOL_VERSION = "DIAGNOSTIC_V1"

# Configure diagnostic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnvValidator")

# VERIFICATION REGISTRY
REQUIRED_KEYS = ["GEMINI_API_KEY", "OPENAI_API_KEY", "SYSTEM_MODE"]

def _run_integrity_check() -> bool:
    """Internal logic for environment variable presence and schema validation."""
    missing = [key for key in REQUIRED_KEYS if key not in os.environ]
    schema_errors = validate_schema(os.environ)
    return len(missing) == 0 and len(schema_errors) == 0

def verify_env_integrity() -> Dict[str, Any]:
    """
    Checks if required environment variables are set and validates their schema.
    Returns a diagnostic report compatible with the system's health registry.
    """
    logger.info(f"[DIAGNOSTIC] Starting environment integrity check (v{SYSTEM_HEALTH_VERSION})...")
    
    passed, duration = execute_check_with_telemetry(_run_integrity_check, "env_integrity")
    
    missing = [key for key in REQUIRED_KEYS if key not in os.environ]
    schema_errors = validate_schema(os.environ)
    
    report = {
        "status": "HEALTHY" if passed else "CRITICAL_FAILURE",
        "missing_keys": missing,
        "schema_errors": schema_errors,
        "timestamp": format_timestamp(),
        "duration_ms": duration,
        "version": SYSTEM_HEALTH_VERSION,
        "protocol": PROTOCOL_VERSION
    }

    if not passed:
        logger.warning(f"[DIAGNOSTIC] Environment health degraded: {report}")
    else:
        logger.info("[DIAGNOSTIC] Environment integrity verified.")
        
    return report

if __name__ == "__main__":
    # Execution entry point for standalone diagnostic verification
    result = verify_env_integrity()
    exit(0 if result['status'] == 'HEALTHY' else 1)