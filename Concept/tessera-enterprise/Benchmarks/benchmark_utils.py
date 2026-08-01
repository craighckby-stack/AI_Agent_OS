"""
BENCHMARK UTILITIES
Role: Telemetry and execution wrappers for benchmark metrics.
"""

import time
from typing import Callable, Dict, Any

def run_with_telemetry(func: Callable) -> Dict[str, Any]:
    """Executes a benchmark function and returns performance metrics."""
    start = time.perf_counter()
    try:
        result = func()
        duration = (time.perf_counter() - start) * 1000
        return {"status": "success", "duration_ms": round(duration, 3), "data": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}