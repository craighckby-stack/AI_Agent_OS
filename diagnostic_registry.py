"""
DIAGNOSTIC REGISTRY
Centralized hub for registering system health checks.
Role: Manages the lifecycle of system integrity probes and provides a registry interface for the diagnostic engine.
Integration: Used by diagnostic_engine.py to verify kernel health.
"""

from typing import Dict, Callable, Any
import logging

# Configure diagnostic logging
logger = logging.getLogger("DiagnosticRegistry")

class DiagnosticRegistry:
    """
    Registry manager for system health checks.
    Implements the 'Diagnostic Integrity Hook' pattern.
    """
    def __init__(self):
        self._checks: Dict[str, Callable[[], bool]] = {}

    def register(self, name: str, check_func: Callable[[], bool]) -> None:
        """Registers a new diagnostic probe."""
        self._checks[name] = check_func
        logger.info(f"[REGISTRY] Registered probe: {name}")

    def unregister(self, name: str) -> None:
        """Removes a diagnostic probe."""
        if name in self._checks:
            del self._checks[name]
            logger.info(f"[REGISTRY] Unregistered probe: {name}")

    def get_all_checks(self) -> Dict[str, Callable[[], bool]]:
        """Returns all registered probes."""
        return self._checks

# Global registry instance
registry = DiagnosticRegistry()

def check_memory_integrity() -> bool:
    """Default memory integrity probe."""
    return True

# Initialize default checks
registry.register('memory_integrity', check_memory_integrity)

# Expose for legacy compatibility
REGISTERED_CHECKS = registry.get_all_checks()