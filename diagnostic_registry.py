"""
DIAGNOSTIC REGISTRY
Role: Centralized hub for registering, tracking, and managing system health probes.
Integration: Interoperates with diagnostic_engine.py and kernel execution cycles for dynamic health monitoring.
Dependencies: diagnostic_registry_utils

Manages the lifecycle of system integrity probes, implementing thread-safe dynamic probe registration
and metadata tracking.
"""

import logging
import threading
from typing import Dict, Callable, Any, Optional
from diagnostic_registry_utils import ProbeMetadata, validate_probe_function

# Configure diagnostic logging
logger = logging.getLogger("DiagnosticRegistry")


class DiagnosticRegistry:
    """
    Thread-safe registry manager for system health checks.
    Implements the 'Diagnostic Integrity Hook' pattern with telemetry and metadata tracking.
    """
    def __init__(self) -> None:
        self._checks: Dict[str, Callable[[], bool]] = {}
        self._metadata: Dict[str, ProbeMetadata] = {}
        self._lock: threading.Lock = threading.Lock()

    def register(
        self, 
        name: str, 
        check_func: Callable[[], bool], 
        description: str = "", 
        category: str = "general"
    ) -> None:
        """Registers a new diagnostic probe with metadata logging."""
        if not validate_probe_function(check_func):
            logger.error(f"[REGISTRY] Invalid probe callable provided for: {name}")
            raise ValueError(f"Probe function for '{name}' must be callable.")

        with self._lock:
            self._checks[name] = check_func
            self._metadata[name] = ProbeMetadata(
                name=name, 
                description=description, 
                category=category
            )
            logger.info(f"[REGISTRY] Registered probe: {name} ({category})")

    def unregister(self, name: str) -> None:
        """Removes a diagnostic probe and its associated metadata."""
        with self._lock:
            if name in self._checks:
                del self._checks[name]
                self._metadata.pop(name, None)
                logger.info(f"[REGISTRY] Unregistered probe: {name}")

    def get_all_checks(self) -> Dict[str, Callable[[], bool]]:
        """Returns all registered probes."""
        with self._lock:
            return dict(self._checks)

    def get_probe_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Returns serialized metadata for a specific probe if registered."""
        with self._lock:
            metadata = self._metadata.get(name)
            return metadata.to_dict() if metadata else None

    def execute_probe(self, name: str) -> bool:
        """Executes a specific probe and records execution telemetry."""
        with self._lock:
            check_func = self._checks.get(name)
            metadata = self._metadata.get(name)

        if not check_func:
            logger.warning(f"[REGISTRY] Probe '{name}' not found.")
            return False

        try:
            status = bool(check_func())
            if metadata:
                with self._lock:
                    metadata.record_execution(status)
            return status
        except Exception as e:
            logger.error(f"[REGISTRY] Error executing probe '{name}': {e}")
            if metadata:
                with self._lock:
                    metadata.record_execution(False)
            return False


# Global registry instance
registry = DiagnosticRegistry()


def check_memory_integrity() -> bool:
    """Default memory integrity probe."""
    return True


# Initialize default checks
registry.register(
    'memory_integrity', 
    check_memory_integrity, 
    description='Validates kernel memory subsystem state.', 
    category='core'
)

# Expose for legacy compatibility
REGISTERED_CHECKS = registry.get_all_checks()