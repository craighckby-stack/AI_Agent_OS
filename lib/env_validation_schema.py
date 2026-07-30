"""
ARCHITECTURAL SCHEMA VALIDATOR
Role: Provides granular validation logic for environment configurations.
"""
from typing import Dict, List, Any

def validate_schema(env: Dict[str, Any]) -> List[str]:
    """
    Performs deep validation on environment variable formats.
    """
    errors = []
    # Example: Validate SYSTEM_MODE is one of the allowed values
    allowed_modes = ['DEVELOPMENT', 'PRODUCTION', 'TEST']
    if env.get('SYSTEM_MODE') and env.get('SYSTEM_MODE') not in allowed_modes:
        errors.append(f"Invalid SYSTEM_MODE: {env.get('SYSTEM_MODE')}")
    
    return errors