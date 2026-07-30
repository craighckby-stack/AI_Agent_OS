"""
ARCHITECTURAL UTILITY: ENV VALIDATOR
Role: Validates that critical environment variables are present and correctly formatted.
Integration: Connects to system diagnostic registry for real-time health monitoring.
Siphoned from: craighckby-stack/AI_Agent_OS
"""
import os
import logging
from typing import Dict, Any
from lib.env_validation_schema import validate_schema

# Configure diagnostic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnvValidator")

REQUIRED_KEYS = ["GEMINI_API_KEY", "OPENAI_API_KEY", "SYSTEM_MODE"]

def verify_env_integrity() -> Dict[str, Any]:
    """
    Checks if required environment variables are set and validates their schema.
    Returns a diagnostic report compatible with the system's health registry.
    """
    logger.info("[DIAGNOSTIC] Starting environment integrity check...")
    
    missing = [key for key in REQUIRED_KEYS if key not in os.environ]
    schema_errors = validate_schema(os.environ)
    
    is_healthy = len(missing) == 0 and len(schema_errors) == 0
    
    report = {
        "status": "HEALTHY" if is_healthy else "CRITICAL_FAILURE",
        "missing_keys": missing,
        "schema_errors": schema_errors,
        "timestamp": "2023-10-27T00:00:00Z" # Placeholder for actual ISO timestamp
    }

    if not is_healthy:
        logger.warning(f"[DIAGNOSTIC] Environment health degraded: {report}")
    else:
        logger.info("[DIAGNOSTIC] Environment integrity verified.")
        
    return report

if __name__ == "__main__":
    verify_env_integrity()