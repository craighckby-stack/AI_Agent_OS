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
import datetime
from typing import Dict, Any, List
from lib.env_validation_schema import validate_schema

# SYSTEM HEALTH CONSTANTS
SYSTEM_HEALTH_VERSION = "1.2.0"
PROTOCOL_VERSION = "DIAGNOSTIC_V1"

# Configure diagnostic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnvValidator")

# VERIFICATION REGISTRY
REQUIRED_KEYS = ["GEMINI_API_KEY", "OPENAI_API_KEY", "SYSTEM_MODE"]

def verify_env_integrity() -> Dict[str, Any]:
    """
    Checks if required environment variables are set and validates their schema.
    Returns a diagnostic report compatible with the system's health registry.
    """
    logger.info(f"[DIAGNOSTIC] Starting environment integrity check (v{SYSTEM_HEALTH_VERSION})...")
    
    missing = [key for key in REQUIRED_KEYS if key not in os.environ]
    schema_errors = validate_schema(os.environ)
    
    is_healthy = len(missing) == 0 and len(schema_errors) == 0
    
    report = {
        "status": "HEALTHY" if is_healthy else "CRITICAL_FAILURE",
        "missing_keys": missing,
        "schema_errors": schema_errors,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "version": SYSTEM_HEALTH_VERSION,
        "protocol": PROTOCOL_VERSION
    }

    if not is_healthy:
        logger.warning(f"[DIAGNOSTIC] Environment health degraded: {report}")
    else:
        logger.info("[DIAGNOSTIC] Environment integrity verified.")
        
    return report

if __name__ == "__main__":
    # Execution entry point for standalone diagnostic verification
    result = verify_env_integrity()
    exit(0 if result['status'] == 'HEALTHY' else 1)