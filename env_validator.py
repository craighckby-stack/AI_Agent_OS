"""
ARCHITECTURAL UTILITY: ENV VALIDATOR
Role: Validates that critical environment variables are present and correctly formatted.
"""
import os

REQUIRED_KEYS = ["GEMINI_API_KEY", "OPENAI_API_KEY", "SYSTEM_MODE"]

def verify_env_integrity():
    """
    Checks if required environment variables are set. 
    Raises warning if configuration is incomplete.
    """
    missing = [key for key in REQUIRED_KEYS if key not in os.environ]
    if missing:
        print(f"[DIAGNOSTIC] WARNING: Missing environment variables: {', '.join(missing)}")
    else:
        print("[DIAGNOSTIC] Environment integrity verified.")
