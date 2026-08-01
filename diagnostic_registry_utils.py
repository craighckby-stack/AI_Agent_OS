"""
DIAGNOSTIC REGISTRY UTILITIES
Role: Helper structures for probe metadata and validation.
Integration: Used by diagnostic_registry.py to manage probe lifecycle.
"""

from typing import Any, Dict, Callable, Optional
import time

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

    def record_execution(self, success: bool) -> None:
        self.last_run = time.time()
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "last_run": self.last_run,
            "success_count": self.success_count,
            "failure_count": self.failure_count
        }