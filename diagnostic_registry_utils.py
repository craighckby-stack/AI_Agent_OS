"""
DIAGNOSTIC REGISTRY UTILITIES
Role: Auxiliary helper utilities and metadata structures for system diagnostic probes.
Integration: Imported by diagnostic_registry.py to handle probe metadata, validation, and registry telemetry.
"""

import time
from typing import Dict, Any, Optional, Callable


class ProbeMetadata:
    """Metadata container for registered diagnostic probes."""
    def __init__(self, name: str, description: str = "", category: str = "general") -> None:
        self.name: str = name
        self.description: str = description
        self.category: str = category
        self.registered_at: float = time.time()
        self.execution_count: int = 0
        self.last_status: Optional[bool] = None

    def record_execution(self, status: bool) -> None:
        """Updates probe execution statistics."""
        self.execution_count += 1
        self.last_status = status

    def to_dict(self) -> Dict[str, Any]:
        """Serializes probe metadata to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "registered_at": self.registered_at,
            "execution_count": self.execution_count,
            "last_status": self.last_status,
        }


def validate_probe_function(check_func: Callable[[], bool]) -> bool:
    """Validates that the check function is a callable object."""
    return callable(check_func)
