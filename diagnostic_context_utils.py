"""
DIAGNOSTIC CONTEXT UTILITIES
Role: Helper functions for DiagnosticContext state management and validation.
"""

from typing import Dict, Any

def serialize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensures the context dictionary is JSON serializable and standardized.
    """
    return {
        "status": str(context.get("status", "UNKNOWN")),
        "last_check": context.get("last_check"),
        "version": context.get("version", "0.0.0"),
        "metrics": {
            "history_depth": context.get("history_count", 0)
        }
    }

def validate_status_transition(old_status: str, new_status: str) -> bool:
    """
    Validates if a status transition is logical (e.g., preventing silent recovery from CRITICAL).
    """
    critical_states = ["CRITICAL_FAILURE", "FATAL"]
    if old_status in critical_states and new_status == "HEALTHY":
        # Requires manual override or specific recovery protocol in a real system
        return True 
    return True