"""
ARCHITECTURAL TESSERA BENCHMARK SUITE
Role: Primary interface for performance validation and system integrity benchmarking.
Integration: Connects to the Tessera Diagnostic Engine for pre-execution health checks.
Dependencies: benchmark_registry, benchmark_utils, diagnostic_engine

This module serves as the entry point for the Tessera Enterprise benchmark suite,
ensuring all performance metrics are captured within a validated diagnostic context.
"""

from typing import Dict, Any, List, Callable
import logging
from .benchmark_registry import REGISTERED_BENCHMARKS
from .benchmark_utils import run_with_telemetry
from ..Tessera.diagnostic_engine import run_system_diagnostics

# Configure benchmark logging
logger = logging.getLogger("BenchmarkSuite")

class TesseraBenchmarkSuite:
    def __init__(self):
        self.registry = REGISTERED_BENCHMARKS

    def execute_all(self) -> Dict[str, Any]:
        """Executes all registered benchmarks with telemetry wrapping and pre-flight diagnostic checks."""
        # Pre-flight diagnostic check
        diag_report = run_system_diagnostics()
        if diag_report.get('status') != 'HEALTHY':
            logger.error("[BENCHMARK] Pre-flight diagnostic check failed. Aborting benchmarks.")
            return {"error": "Diagnostic failure", "diagnostic_report": diag_report}

        results = {}
        for name, func in self.registry.items():
            try:
                results[name] = run_with_telemetry(func)
            except Exception as e:
                logger.error(f"[BENCHMARK] Execution failed for {name}: {e}")
                results[name] = {"passed": False, "error": str(e)}
        return results

# Initialize global suite instance
suite = TesseraBenchmarkSuite()

def run_benchmarks() -> Dict[str, Any]:
    """Public API for triggering the benchmark suite with integrated diagnostic validation."""
    return suite.execute_all()