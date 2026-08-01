"""
DIAGNOSTIC CONTEXT UTILITIES
Role: Helper functions for state serialization and transition validation.
Integration: Used by diagnostic_context.py to maintain state integrity.
"""

from typing import Dict, Any, List

def serialize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures context data is sanitized for reporting."""
    return {k: v for k, v in context.items() if v is not None}

def validate_status_transition(old_status: str, new_status: str) -> bool:
    """Validates that the system state transition is logical."""
    # Simple transition logic: allow any transition for now
    return True