"""
BENCHMARK REGISTRY
Role: Centralized registry for all Tessera performance benchmarks.
Integration: Connects with Benchmark Utilities for telemetry and reporting.
"""

from __future__ import annotations
import time
from typing import Dict, Callable, Any, List
from .benchmark_utils import BenchmarkResult, format_benchmark_report

# Registry for all performance benchmarks
REGISTERED_BENCHMARKS: Dict[str, Callable] = {}

def register_benchmark(name: str):
    """
    Decorator to register a benchmark function.
    Usage: @register_benchmark('latency_test')
    """
    def decorator(func: Callable):
        REGISTERED_BENCHMARKS[name] = func
        return func
    return decorator

def run_benchmarks() -> Dict[str, Any]:
    """
    Executes all registered benchmarks and returns a structured telemetry report.
    """
    results: List[BenchmarkResult] = []
    
    for name, func in REGISTERED_BENCHMARKS.items():
        start_time = time.perf_counter()
        try:
            # Execute benchmark
            metadata = func()
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            results.append(BenchmarkResult(
                name=name,
                passed=True,
                duration_ms=round(duration_ms, 3),
                metadata=metadata or {}
            ))
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            results.append(BenchmarkResult(
                name=name,
                passed=False,
                duration_ms=round(duration_ms, 3),
                metadata={"error": str(e)}
            ))
            
    return format_benchmark_report(results)

def get_registered_benchmark_names() -> List[str]:
    """Returns a list of all currently registered benchmark identifiers."""
    return list(REGISTERED_BENCHMARKS.keys())