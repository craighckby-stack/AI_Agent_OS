"""
ARCHITECTURAL TESSERA BENCHMARK SUITE
Role: Primary interface for performance validation and system integrity benchmarking.
Integration: Connects to the Tessera Diagnostic Engine for pre-execution health checks.
Dependencies: benchmark_registry, benchmark_utils

This module serves as the entry point for the Tessera Enterprise benchmark suite,
ensuring all performance metrics are captured within a validated diagnostic context.
"""

from typing import Dict, Any, List, Callable
from .benchmark_registry import REGISTERED_BENCHMARKS
from .benchmark_utils import run_with_telemetry

class TesseraBenchmarkSuite:
    def __init__(self):
        self.registry = REGISTERED_BENCHMARKS

    def execute_all(self) -> Dict[str, Any]:
        """Executes all registered benchmarks with telemetry wrapping."""
        results = {}
        for name, func in self.registry.items():
            results[name] = run_with_telemetry(func)
        return results

# Initialize global suite instance
suite = TesseraBenchmarkSuite()

def run_benchmarks() -> Dict[str, Any]:
    """Public API for triggering the benchmark suite."""
    return suite.execute_all()