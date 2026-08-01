"""
DIAGNOSTIC REGISTRY UTILITIES
Role: Helper structures for probe metadata, validation, and lifecycle management.
Integration: Used by diagnostic_registry.py to manage probe lifecycle and telemetry.
"""

from typing import Any, Dict, Callable, Optional
import time
from enum import Enum

class ProbeStatus(Enum):
    INITIALIZED = "INITIALIZED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ProbeRegistryError(Exception):
    """Custom exception for registry-level failures."""
    pass

def validate_probe_function(func: Callable) -> bool:
    """Validates that a probe function is callable."""
    return callable(func)

class ProbeMetadata:
    def __init__(self, name: str, description: str, category: str) -> None:
        self.name = name
        self.description = description
        self.category = category
        self.last_run: Optional[float] = None
        self.success_count: int = 0
        self.failure_count: int = 0
        self.status: ProbeStatus = ProbeStatus.INITIALIZED

    def record_execution(self, success: bool) -> None:
        self.last_run = time.time()
        if success:
            self.success_count += 1
            self.status = ProbeStatus.COMPLETED
        else:
            self.failure_count += 1
            self.status = ProbeStatus.FAILED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "last_run": self.last_run,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "status": self.status.value
        }

    def to_json(self) -> Dict[str, Any]:
        """Alias for to_dict for serialization compatibility."""
        return self.to_dict()