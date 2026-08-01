"""
DIAGNOSTIC CONTEXT UTILITIES
Role: Helper functions for state serialization, transition validation, and snapshot generation.
Integration: Used by diagnostic_context.py to maintain state integrity and provide diagnostic observability.
"""

from typing import Dict, Any, List, Optional
import copy

# Valid state machine transitions to prevent illegal system state jumps
ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
    "INITIALIZING": ["HEALTHY", "CRITICAL_FAILURE"],
    "HEALTHY": ["HEALTHY", "CRITICAL_FAILURE", "DEGRADED"],
    "DEGRADED": ["HEALTHY", "CRITICAL_FAILURE"],
    "CRITICAL_FAILURE": ["INITIALIZING"]
}

def serialize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures context data is sanitized, deep-copied, and filtered for reporting."""
    sanitized = {k: v for k, v in context.items() if v is not None}
    return copy.deepcopy(sanitized)

def validate_status_transition(old_status: str, new_status: str) -> bool:
    """Validates that the system state transition is logical based on the defined state machine."""
    if old_status not in ALLOWED_TRANSITIONS:
        return True
    return new_status in ALLOWED_TRANSITIONS.get(old_status, [])

def generate_context_snapshot(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a high-fidelity snapshot of the current diagnostic context.
    Used for post-mortem analysis and error reporting.
    """
    return {
        "snapshot_data": serialize_context(context),
        "snapshot_version": "1.0.0-SNAPSHOT"
    }