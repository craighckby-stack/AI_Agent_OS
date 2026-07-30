"""
ENVIRONMENT SCHEMA VALIDATOR
Role: Validates the integrity of loaded environment variables against required schemas.
Integration: Called by env_diagnostic_utils.py.
"""

from typing import Tuple, Dict, Any
import os

def validate_env_schema() -> Tuple[bool, Dict[str, Any]]:
    """
    Performs schema-based validation of environment variables.
    Returns (is_valid, details).
    """
    # Define required keys for system integrity
    required_keys = ["API_KEY", "DB_URL"]
    missing = [key for key in required_keys if key not in os.environ]
    
    is_valid = len(missing) == 0
    details = {
        "missing_keys": missing,
        "total_checked": len(required_keys)
    }
    
    return is_valid, details