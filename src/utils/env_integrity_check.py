"""
ENVIRONMENT INTEGRITY CHECKER
Role: Validates the .env file against the .env.example manifest.
Integration: Called by the DiagnosticEngine during the 'env_loader' check phase.
"""

import os
import logging
from typing import Dict, List, Set

logger = logging.getLogger("EnvIntegrity")

def get_required_keys(example_path: str = ".env.example") -> Set[str]:
    """Parses the example file to identify required configuration keys."""
    required_keys = set()
    if not os.path.exists(example_path):
        return required_keys
        
    with open(example_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=")[0].strip()
                required_keys.add(key)
    return required_keys

def validate_env_integrity(env_path: str = ".env", example_path: str = ".env.example") -> Dict[str, any]:
    """
    Performs a structural integrity check on the environment file.
    Returns a diagnostic result compatible with the DiagnosticEngine.
    """
    required = get_required_keys(example_path)
    missing = []
    
    if not os.path.exists(env_path):
        return {
            "passed": False,
            "message": f"Critical Failure: {env_path} not found.",
            "missing_keys": list(required)
        }

    # Load current env keys
    current_keys = set()
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                current_keys.add(line.split("=")[0].strip())

    missing = [key for key in required if key not in current_keys]
    
    passed = len(missing) == 0
    return {
        "passed": passed,
        "message": "Environment integrity verified." if passed else f"Missing {len(missing)} required keys.",
        "missing_keys": missing,
        "metadata": {
            "required_count": len(required),
            "present_count": len(current_keys)
        }
    }
