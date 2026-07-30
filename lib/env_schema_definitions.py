"""
ENVIRONMENT SCHEMA DEFINITIONS
Role: Centralized configuration rules for system environment variables.
"""

SCHEMA_RULES = {
    "SYSTEM_MODE": {
        "allowed": ["DEVELOPMENT", "PRODUCTION", "TEST"],
        "required": True
    },
    "LOG_LEVEL": {
        "allowed": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "required": False
    }
}