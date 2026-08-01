"""
DIAGNOSTIC CONTEXT UTILS
Role: Helper utilities for diagnostic state serialization, transition validation, and integrity enforcement.
Integration: Delegated from diagnostic_context.py to maintain modularity and ensure state consistency.
Dependencies: None (Core utility layer).
"""

from __future__ import annotations
from typing import Dict, Any, Final
import datetime

# Constants for state governance
VALID_STATUSES: Final[list[str]] = ["INITIALIZING", "HEALTHY", "DEGRADED", "CRITICAL_FAILURE", "ERROR"]

def serialize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serializes diagnostic context with integrity metadata.
    Ensures all snapshots are timestamped and marked for audit.
    """
    return {
        "data": context,
        "serialized": True,
        "serialization_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "integrity_hash": hash(frozenset(context.items()))
    }

def validate_status_transition(old_status: str, new_status: str) -> bool:
    """
    Validates if a status transition is logically sound based on system governance.
    Prevents illegal state jumps (e.g., ERROR -> HEALTHY without re-initialization).
    """
    if new_status not in VALID_STATUSES:
        return False
    
    # Governance: Cannot transition to HEALTHY from ERROR without explicit reset
    if old_status == "ERROR" and new_status == "HEALTHY":
        return False
        
    return True

def sanitize_context_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prunes sensitive or redundant keys from diagnostic context before serialization.
    """
    return {k: v for k, v in data.items() if not k.startswith("_")}