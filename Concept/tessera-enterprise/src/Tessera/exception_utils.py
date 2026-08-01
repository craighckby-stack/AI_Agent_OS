"""
EXCEPTION UTILITIES
Role: Provides diagnostic context snapshots for exception handling.
Integration: Imported by exceptions.py to ensure error telemetry is captured.
"""

from typing import Dict, Any
import time

def get_diagnostic_context_snapshot() -> Dict[str, Any]:
    """Captures a point-in-time snapshot of the system state for error reporting."""
    return {
        "timestamp": time.time(),
        "system_state": "active",
        "trace_id": hex(id(time.time())),
        "version": "1.0.0-DIAGNOSTIC-AWARE"
    }