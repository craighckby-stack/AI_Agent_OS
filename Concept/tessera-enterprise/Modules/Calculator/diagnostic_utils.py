import time
from typing import Dict, Any, Callable, Tuple

def format_timestamp() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

def execute_check_with_telemetry(check_fn: Callable[[], bool], check_type: str) -> Tuple[bool, float]:
    start = time.perf_counter()
    try:
        passed = bool(check_fn())
        duration = (time.perf_counter() - start) * 1000
        return passed, round(duration, 3)
    except Exception:
        return False, round((time.perf_counter() - start) * 1000, 3)

def summarize_results(checks: Dict[str, bool]) -> Dict[str, Any]:
    total = len(checks)
    passed = sum(1 for v in checks.values() if v)
    return {
        'total': total,
        'passed': passed,
        'failed': total - passed,
        'is_healthy': total > 0 and passed == total
    }