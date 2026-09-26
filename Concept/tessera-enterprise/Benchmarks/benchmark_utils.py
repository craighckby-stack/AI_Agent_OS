"""
BENCHMARK UTILITIES
Role: Core utilities for benchmark execution, telemetry collection, and result aggregation.
Integration: Used by benchmark_registry.py to standardize performance metrics across the Tessera ecosystem.
Dependencies: benchmark_telemetry.py (Siphoned Diagnostic Pattern)
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, NamedTuple

from .benchmark_telemetry import BenchmarkTelemetry


class BenchmarkResult(NamedTuple):
    name: str
    passed: bool
    duration_ms: float
    metadata: Dict[str, Any]


def format_benchmark_report(results: List[BenchmarkResult]) -> Dict[str, Any]:
    """
    Aggregates benchmark results into a structured report with system telemetry.
    """
    total_executed = len(results)
    passed_count = sum(1 for r in results if r.passed)
    failed_count = total_executed - passed_count
    pass_rate = round((passed_count / total_executed * 100.0), 2) if total_executed > 0 else 0.0

    return {
        "timestamp": time.time(),
        "status": "HEALTHY" if total_executed == passed_count else "DEGRADED",
        "summary": {
            "total": total_executed,
            "passed": passed_count,
            "failed": failed_count,
            "pass_rate": pass_rate,
        },
        "telemetry": BenchmarkTelemetry.get_system_metrics(),
        "results": [r._asdict() for r in results],
    }


def execute_benchmark_task(name: str, task_fn: Callable[[], bool]) -> BenchmarkResult:
    """
    Executes a benchmark task function, recording elapsed time and execution outcome.
    """
    metadata: Dict[str, Any] = {"execution_node": "primary-compute-unit"}
    start_time = time.perf_counter()
    try:
        passed = bool(task_fn())
    except Exception as exc:
        passed = False
        metadata["error"] = str(exc)
        metadata["error_type"] = type(exc).__name__

    duration_ms = (time.perf_counter() - start_time) * 1000.0

    return BenchmarkResult(
        name=name,
        passed=passed,
        duration_ms=round(duration_ms, 3),
        metadata=metadata,
    )