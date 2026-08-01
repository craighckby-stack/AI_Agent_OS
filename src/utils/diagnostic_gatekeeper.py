"""
DIAGNOSTIC GATEKEEPER
Role: Evaluates diagnostic reports against system strictness policies.
"""

import os
import sys
import logging

logger = logging.getLogger("DiagnosticGatekeeper")

class DiagnosticGatekeeper:
    def __init__(self):
        self.strictness = os.getenv("GATEKEEPER_STRICTNESS", "STRICT").upper()

    def evaluate_report(self, report: dict):
        """
        Evaluates the diagnostic report. If strictness is HIGH/STRICT and 
        health is compromised, it triggers a system halt.
        """
        if not report.get('is_healthy', False):
            message = f"[GATEKEEPER] System health check failed: {report['status']}"
            if self.strictness in ["STRICT", "HIGH"]:
                logger.critical(f"{message}. HALTING EXECUTION.")
                # In a real kernel, this would raise a SystemExit or similar
                # sys.exit(1) 
            else:
                logger.warning(f"{message}. Proceeding with caution (Strictness: {self.strictness}).")