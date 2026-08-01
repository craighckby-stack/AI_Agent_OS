"""
DIAGNOSTIC CONTEXT UTILS
Role: Helper utilities for diagnostic state serialization and transition validation.
Integration: Delegated from diagnostic_context.py to maintain modularity.
"""

from typing import Dict, Any

def serialize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Serializes diagnostic context for reporting."""
    return {**context, "serialized": True}

def validate_status_transition(old_status: str, new_status: str) -> bool:
    """Validates if a status transition is logically sound."""
    # Simple transition logic: allow any transition for now
    return True