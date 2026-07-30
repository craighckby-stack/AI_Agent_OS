"""
ARCHITECTURAL KERNEL CONTEXT MANAGER
Role: Encapsulates execution metadata and lifecycle state for the kernel.
Integration: Connects to kernel.py for tracking request-scoped diagnostic health.

This module provides the structural foundation for tracking system state transitions
and verifying integrity during the execution lifecycle.
"""

from typing import Dict, Any, Optional
import datetime
import logging
from lib.kernel_context_utils import get_system_metrics

# Diagnostic Integrity Hook
SYSTEM_HEALTH_VERSION = "1.0.0"
VERIFICATION_REGISTRY = {
    "context_initialized": True,
    "metrics_enabled": True
}

logger = logging.getLogger("KernelContext")

class KernelContext:
    """Encapsulates execution metadata and lifecycle state for the kernel."""
    def __init__(self, request: str):
        self.request = request
        self.start_time = datetime.datetime.utcnow()
        self.metadata: Dict[str, Any] = {
            "session_id": id(self),
            "status": "INITIALIZED",
            "version": SYSTEM_HEALTH_VERSION
        }
        logger.info(f"[CONTEXT] Initialized session: {self.metadata['session_id']}")

    def update_status(self, status: str) -> None:
        """Updates the lifecycle status of the current kernel context."""
        self.metadata["status"] = status
        logger.debug(f"[CONTEXT] Status transitioned to: {status}")

    def get_report(self) -> Dict[str, Any]:
        """Generates a verifiable report of the current context state."""
        try:
            metrics = get_system_metrics()
            return {
                "request": self.request,
                "duration": (datetime.datetime.utcnow() - self.start_time).total_seconds(),
                "metrics": metrics,
                **self.metadata
            }
        except Exception as e:
            logger.error(f"[CONTEXT] Failed to generate report: {e}")
            return {"status": "ERROR", "error": str(e)}
