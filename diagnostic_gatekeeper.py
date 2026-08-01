"""
DIAGNOSTIC GATEKEEPER
Role: Enforces system health policies and critical failure thresholds.
Integration: Used by diagnostic_engine.py to prevent kernel execution on critical failure.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("DiagnosticGatekeeper")

class DiagnosticGatekeeper:
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode

    def evaluate_report(self, report: Dict[str, Any]) -> bool:
        """Evaluates if the system state allows for continued execution."""
        if report.get('status') == 'CRITICAL_FAILURE':
            logger.critical("[GATEKEEPER] Critical failure detected. Halting execution.")
            if self.strict_mode:
                # In a real kernel, this would raise a SystemExit or trigger a recovery sequence
                return False
        return True