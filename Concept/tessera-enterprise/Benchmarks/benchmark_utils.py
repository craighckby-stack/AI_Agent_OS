"""
BENCHMARK UTILITIES
Role: Core utilities for benchmark execution, telemetry collection, and result aggregation.
Integration: Used by benchmark_registry.py to standardize performance metrics across the Tessera ecosystem.
Dependencies: benchmark_telemetry.py (Siphoned Diagnostic Pattern)
"""

from __future__ import annotations
import time
from typing import Any, Dict, NamedTuple, List, Callable
from .benchmark_telemetry import BenchmarkTelemetry

class BenchmarkResult(NamedTuple):
    name: str
    passed: bool
    duration_ms: float
    metadata: Dict[str, Any]

def format_benchmark_report(results: List[BenchmarkResult]) -> Dict[str, Any]:
    """
    Aggregates benchmark results into a structured, telemetry-rich report.
    Aligns with the enterprise diagnostic engine schema.
    """
    total_executed = len(results)
    passed_count = sum(1 for r in results if r.passed)
    
    return {
        "timestamp": time.time(),
        "status": "HEALTHY" if total_executed == passed_count else "DEGRADED",
        "summary": {
            "total": total_executed,
            "passed": passed_count,
            "failed": total_executed - passed_count,
            "pass_rate": round((passed_count / total_executed * 100), 2) if total_executed > 0 else 0.0
        },
        "telemetry": BenchmarkTelemetry.get_system_metrics(),
        "results": [r._asdict() for r in results]
    }

def execute_benchmark_task(name: str, task_fn: Callable[[], bool]) -> BenchmarkResult:
    """
    Executes a specific benchmark task with high-precision timing and error handling.
    """
    start_time = time.perf_counter()
    try:
        passed = bool(task_fn())
    except Exception as e:
        passed = False
    
    duration_ms = (time.perf_counter() - start_time) * 1000.0
    
    return BenchmarkResult(
        name=name,
        passed=passed,
        duration_ms=round(duration_ms, 3),
        metadata={"execution_node": "primary-compute-unit"}
    )