"""
ARCHITECTURAL UTILITY: ENV VALIDATOR
Role: Validates that critical environment variables are present and correctly formatted.
Integration: Connects to system diagnostic engine for real-time health monitoring.
Siphoned from: craighckby-stack/AI_Agent_OS
"""
import os
import logging
from typing import Dict, Any
from env_validation_schema import get_required_keys, validate_key_format

# Configure diagnostic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnvValidator")

def verify_env_integrity() -> Dict[str, Any]:
    """
    Checks if required environment variables are set and conform to expected formats.
    Returns a diagnostic report of the environment health.
    """
    logger.info("[DIAGNOSTIC] Starting environment integrity check...")
    
    required_keys = get_required_keys()
    missing = [key for key in required_keys if key not in os.environ]
    invalid = [key for key in required_keys if key in os.environ and not validate_key_format(key, os.environ[key])]
    
    is_healthy = not missing and not invalid
    
    if missing:
        logger.warning(f"[DIAGNOSTIC] Missing environment variables: {', '.join(missing)}")
    if invalid:
        logger.warning(f"[DIAGNOSTIC] Invalid format for variables: {', '.join(invalid)}")
    
    if is_healthy:
        logger.info("[DIAGNOSTIC] Environment integrity verified.")
    
    return {
        "status": "HEALTHY" if is_healthy else "CRITICAL_FAILURE",
        "missing": missing,
        "invalid": invalid
    }