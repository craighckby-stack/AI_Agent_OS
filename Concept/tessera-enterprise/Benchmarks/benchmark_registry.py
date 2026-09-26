"""
BENCHMARK REGISTRY
Role: Centralized registry for all Tessera performance benchmarks.
Integration: Connects with Benchmark Utilities for telemetry and reporting.
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, Dict, List, Mapping, Optional, TypeVar

from .benchmark_utils import BenchmarkResult, format_benchmark_report

logger = logging.getLogger(__name__)

BenchmarkCallable = Callable[[], Optional[Mapping[str, Any]]]
F = TypeVar("F", bound=Callable[..., Any])

# Registry for all performance benchmarks
REGISTERED_BENCHMARKS: Dict[str, BenchmarkCallable] = {}


def register_benchmark(name: str) -> Callable[[F], F]:
    """
    Decorator to register a benchmark function.
    
    Usage:
        @register_benchmark('latency_test')
        def my_benchmark():
            ...
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Benchmark name must be a non-empty string.")

    def decorator(func: F) -> F:
        REGISTERED_BENCHMARKS[name] = func
        return functools.wraps(func)(func)

    return decorator


def run_benchmarks() -> Dict[str, Any]:
    """
    Executes all registered benchmarks safely and returns a structured telemetry report.
    """
    results: List[BenchmarkResult] = []
    benchmarks_snapshot = tuple(REGISTERED_BENCHMARKS.items())

    for name, func in benchmarks_snapshot:
        start_time = time.perf_counter()
        try:
            raw_metadata = func()
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            
            metadata: Dict[str, Any] = (
                dict(raw_metadata) if isinstance(raw_metadata, Mapping) else {}
            )
            
            results.append(
                BenchmarkResult(
                    name=name,
                    passed=True,
                    duration_ms=round(duration_ms, 3),
                    metadata=metadata,
                )
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.exception("Benchmark '%s' encountered an unhandled exception.", name)
            results.append(
                BenchmarkResult(
                    name=name,
                    passed=False,
                    duration_ms=round(duration_ms, 3),
                    metadata={
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                    },
                )
            )

    return format_benchmark_report(results)


def get_registered_benchmark_names() -> List[str]:
    """Returns a list of all currently registered benchmark identifiers."""
    return list(REGISTERED_BENCHMARKS.keys())