from __future__ import annotations
import time
from typing import Any, Dict, NamedTuple

class BenchmarkResult(NamedTuple):
    name: str
    passed: bool
    duration_ms: float
    metadata: Dict[str, Any]

def format_benchmark_report(results: list[BenchmarkResult]) -> Dict[str, Any]:
    """Aggregates benchmark results into a structured report."""
    return {
        "timestamp": time.time(),
        "total_executed": len(results),
        "passed_count": sum(1 for r in results if r.passed),
        "results": [r._asdict() for r in results]
    }