"""
DIAGNOSTIC REGISTRY UTILITIES
Role: Auxiliary helper utilities and metadata structures for system diagnostic probes.
Integration: Imported by diagnostic_registry.py to handle probe metadata, validation, and registry telemetry.

This module provides the structural foundation for the Diagnostic Registry, 
enforcing strict validation and telemetry tracking for all system probes.
"""

import time
from typing import Dict, Any, Optional, Callable

class ProbeRegistryError(Exception):
    """Custom exception for diagnostic registry failures."""
    pass

class ProbeMetadata:
    """Metadata container for registered diagnostic probes with telemetry tracking."""
    def __init__(self, name: str, description: str = "", category: str = "general") -> None:
        self.name: str = name
        self.description: str = description
        self.category: str = category
        self.registered_at: float = time.time()
        self.execution_count: int = 0
        self.last_status: Optional[bool] = None

    def record_execution(self, status: bool) -> None:
        """Updates probe execution statistics and status."""
        self.execution_count += 1
        self.last_status = status

    def to_dict(self) -> Dict[str, Any]:
        """Serializes probe metadata to a dictionary for system reporting."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "registered_at": self.registered_at,
            "execution_count": self.execution_count,
            "last_status": self.last_status,
        }

    def to_json(self) -> Dict[str, Any]:
        """Alias for to_dict for compatibility with JSON-based diagnostic engines."""
        return self.to_dict()


def validate_probe_function(check_func: Callable[[], bool]) -> bool:
    """Validates that the check function is a callable object."""
    if not callable(check_func):
        raise ProbeRegistryError(f"Invalid probe function provided: {type(check_func)}")
    return True


def generate_probe_telemetry() -> Dict[str, Any]:
    """Generates standard telemetry metadata for diagnostic registry operations."""
    return {
        "version": "1.0.0-DIAGNOSTIC-AWARE",
        "system_time": time.time(),
        "registry_status": "active"
    }