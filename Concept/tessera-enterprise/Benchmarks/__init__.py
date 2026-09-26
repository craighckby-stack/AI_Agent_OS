"""
ARCHITECTURAL TESSERA BENCHMARK SUITE
Role: Primary interface for performance validation and system integrity benchmarking.
Integration: Connects to the Tessera Diagnostic Engine for pre-execution health checks.
Dependencies: benchmark_registry, benchmark_utils, diagnostic_engine

This module serves as the entry point for the Tessera Enterprise benchmark suite,
ensuring all performance metrics are captured within a validated diagnostic context.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Final, Mapping

from .benchmark_registry import REGISTERED_BENCHMARKS
from .benchmark_utils import run_with_telemetry
from ..Tessera.diagnostic_engine import run_system_diagnostics

__all__ = [
    "TesseraBenchmarkSuite",
    "suite",
    "run_benchmarks",
]

# Configure benchmark logging
logger: Final[logging.Logger] = logging.getLogger("BenchmarkSuite")
_HEALTHY_STATUS: Final[str] = "HEALTHY"


class TesseraBenchmarkSuite:
    """Enterprise benchmark suite orchestrator with diagnostic pre-flight verification."""

    __slots__ = ("registry",)

    def __init__(self, registry: Mapping[str, Callable[..., Any]] | None = None) -> None:
        self.registry: Mapping[str, Callable[..., Any]] = (
            REGISTERED_BENCHMARKS if registry is None else registry
        )

    def execute_all(self) -> Dict[str, Any]:
        """Executes all registered benchmarks with telemetry wrapping and pre-flight diagnostic checks."""
        try:
            diag_report: Dict[str, Any] = run_system_diagnostics()
        except Exception as diag_err:
            logger.exception("[BENCHMARK] Pre-flight diagnostic engine execution failed.")
            return {
                "error": "Diagnostic execution exception",
                "diagnostic_report": {"status": "UNHEALTHY", "exception": str(diag_err)},
            }

        if diag_report.get("status") != _HEALTHY_STATUS:
            logger.error("[BENCHMARK] Pre-flight diagnostic check failed. Aborting benchmarks.")
            return {"error": "Diagnostic failure", "diagnostic_report": diag_report}

        results: Dict[str, Any] = {}
        for name, func in self.registry.items():
            try:
                results[name] = run_with_telemetry(func)
            except Exception as e:
                logger.error("[BENCHMARK] Execution failed for %s: %s", name, e, exc_info=True)
                results[name] = {"passed": False, "error": str(e)}

        return results


# Initialize global suite instance
suite: Final[TesseraBenchmarkSuite] = TesseraBenchmarkSuite()


def run_benchmarks() -> Dict[str, Any]:
    """Public API for triggering the benchmark suite with integrated diagnostic validation."""
    return suite.execute_all()