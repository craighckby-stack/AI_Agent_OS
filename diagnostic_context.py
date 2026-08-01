"""
DIAGNOSTIC CONTEXT MANAGER
Role: Maintains the state of system health across execution cycles.
Integration: Primary state provider for the DiagnosticEngine and Kernel monitoring.
Siphoned from: craighckby-stack/AI_Agent_OS
"""

import datetime
import threading
from typing import Dict, Any, Optional, List
from diagnostic_context_utils import serialize_context, validate_status_transition

# Architectural constant for system health versioning
SYSTEM_HEALTH_VERSION = "1.1.0"

class DiagnosticContext:
    """
    Thread-safe manager for system health state and diagnostic history.
    Ensures deterministic state tracking across asynchronous execution cycles.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self.last_status = "UNKNOWN"
        self.last_check: Optional[str] = None
        self.history: List[Dict[str, Any]] = []
        self.version = SYSTEM_HEALTH_VERSION

    def update_status(self, status: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Updates the current system status with thread-safety and validation.
        """
        with self._lock:
            if not validate_status_transition(self.last_status, status):
                # Log transition anomaly but proceed with update
                pass

            self.last_status = status
            self.last_check = datetime.datetime.utcnow().isoformat() + 'Z'
            
            entry = {
                "status": self.last_status,
                "timestamp": self.last_check,
                "metadata": metadata or {}
            }
            
            self.history.append(entry)
            # Keep history pruned to last 50 cycles to prevent memory bloat
            if len(self.history) > 50:
                self.history.pop(0)

    def get_context(self) -> Dict[str, Any]:
        """
        Returns a serialized snapshot of the current diagnostic state.
        """
        with self._lock:
            raw_context = {
                "status": self.last_status,
                "last_check": self.last_check,
                "version": self.version,
                "history_count": len(self.history)
            }
            return serialize_context(raw_context)

    def clear_history(self):
        """
        Resets the diagnostic history log.
        """
        with self._lock:
            self.history = []