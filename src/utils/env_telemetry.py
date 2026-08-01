"""
ENV TELEMETRY UTILITY
Role: Measures and reports the performance and health of environment loading cycles.
Siphoned from: AI_Agent_OS/diagnostic_engine_utils.py
"""

import time
import datetime
from typing import Dict, Any, Tuple, Callable

class EnvTelemetry:
    def __init__(self):
        self.start_time = 0.0

    def measure_execution(self, func: Callable[[], bool]) -> Tuple[bool, float]:
        """Executes a function and returns (success, duration_ms)."""
        self.start_time = time.perf_counter()
        try:
            success = func()
            duration_ms = (time.perf_counter() - self.start_time) * 1000.0
            return success, round(duration_ms, 4)
        except Exception:
            duration_ms = (time.perf_counter() - self.start_time) * 1000.0
            return False, round(duration_ms, 4)

    def generate_report(self, success: bool, duration: float) -> Dict[str, Any]:
        """Generates a structured telemetry report."""
        return {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "success": success,
            "duration_ms": duration,
            "status": "OPTIMAL" if duration < 50 else "DEGRADED",
            "engine_version": "1.1.0"
        }