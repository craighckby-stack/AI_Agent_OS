"""
EXCEPTION UTILITIES
Role: Provides diagnostic context snapshots for error reporting.
Integration: Imported by exceptions.py to enrich error metadata.
"""

from typing import Any, Dict
import datetime

def get_diagnostic_context_snapshot() -> Dict[str, Any]:
    """Captures a lightweight snapshot of the current system state for error reporting."""
    return {
        "timestamp": datetime.datetime.utcnow().isoformat() + 'Z',
        "source": "Tessera.exceptions",
        "system_state": "active"
    }