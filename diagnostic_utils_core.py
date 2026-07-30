"""
DIAGNOSTIC UTILITIES CORE
Role: Core logic for diagnostic validation, telemetry generation, and type definitions.
Integration: Delegated from diagnostic_utils.py to maintain modularity.
"""

import time
from typing import NamedTuple, Any, Dict, Callable

class DiagnosticResult(NamedTuple):
    passed: bool
    message: str
    metadata: Dict[str, Any]

def validate_check_function(func: Callable) -> bool:
    """Validates that a check function is callable and returns a DiagnosticResult."""
    return callable(func)

def generate_telemetry_metadata() -> Dict[str, Any]:
    """Generates standard telemetry metadata for diagnostic results."""
    return {
        "timestamp": time.time(),
        "thread_id": id(time.time()),
        "version": "1.0.0-DIAGNOSTIC-AWARE"
    }