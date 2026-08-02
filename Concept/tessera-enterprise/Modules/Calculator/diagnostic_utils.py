from __future__ import annotations
import time
from typing import Dict, Any, Callable, Tuple

def execute_check_with_telemetry(check_fn: Callable[[], bool], check_type: str) -> Tuple[bool, float]:
    start_time = time.perf_counter()
    try:
        passed = bool(check_fn())
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        return passed, round(duration_ms, 3)
    except Exception:
        return False, round((time.perf_counter() - start_time) * 1000.0, 3)

def format_diagnostic_report(status: str, checks: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": status,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "checks": checks,
        "version": "1.0.0-DIAGNOSTIC-AWARE"
    }