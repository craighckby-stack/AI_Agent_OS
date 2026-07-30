"""
UTILITY HELPERS FOR KERNEL CONTEXT
Role: Provides lightweight diagnostic metrics and serialization helpers.
"""

import os
import psutil
from typing import Dict, Any

def get_system_metrics() -> Dict[str, Any]:
    """Returns current system resource utilization for diagnostic reporting."""
    try:
        process = psutil.Process(os.getpid())
        return {
            "memory_usage_mb": process.memory_info().rss / (1024 * 1024),
            "cpu_percent": process.cpu_percent(interval=None)
        }
    except Exception:
        return {"memory_usage_mb": 0, "cpu_percent": 0}
