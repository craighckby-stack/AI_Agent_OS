"""
DIAGNOSTIC UTILITIES CORE
Role: Core logic for diagnostic validation, telemetry generation, and type definitions.
Integration: Delegated from diagnostic_utils.py to maintain modularity and provide a unified schema for system health reporting.
"""

import time
import uuid
from typing import NamedTuple, Any, Dict, Callable, Optional
from enum import Enum

class DiagnosticSeverity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class DiagnosticResult(NamedTuple):
    passed: bool
    message: str
    metadata: Dict[str, Any]

class DiagnosticReport(NamedTuple):
    id: str
    severity: DiagnosticSeverity
    result: DiagnosticResult
    timestamp: float

def validate_check_function(func: Callable) -> bool:
    """Validates that a check function is callable."""
    return callable(func)

def generate_telemetry_metadata(severity: DiagnosticSeverity = DiagnosticSeverity.INFO) -> Dict[str, Any]:
    """Generates standard telemetry metadata for diagnostic results with unique session tracking."""
    return {
        "timestamp": time.time(),
        "thread_id": id(time.time()),
        "version": "1.1.0-DIAGNOSTIC-HARDENED",
        "session_id": str(uuid.uuid4()),
        "severity": severity.value
    }

def create_diagnostic_report(passed: bool, message: str, severity: DiagnosticSeverity = DiagnosticSeverity.INFO) -> DiagnosticReport:
    """Factory method to create a standardized diagnostic report."""
    return DiagnosticReport(
        id=str(uuid.uuid4()),
        severity=severity,
        result=DiagnosticResult(passed=passed, message=message, metadata=generate_telemetry_metadata(severity)),
        timestamp=time.time()
    )