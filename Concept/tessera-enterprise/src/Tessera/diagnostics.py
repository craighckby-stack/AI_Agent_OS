"""
Tessera Enterprise Diagnostics Engine
Role: Validates system integrity, cache persistence layers, and module directory status.
Integration: Called by the kernel (verify_integrity) before processing any request.
             Connects to config.py and cache.py for real-time system health monitoring.
Dependencies: .diagnostic_engine_utils, .diagnostic_utils_core

This engine acts as the primary gatekeeper for system health, ensuring all 
critical dependencies are verified before kernel execution cycles.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

from .diagnostic_engine_utils import (
    execute_check_with_telemetry,
    summarize_diagnostic_results,
)

logger = logging.getLogger("tessera.diagnostics")


@dataclass
class DiagnosticReport:
    """Result of a diagnostic run."""

    status: str  # "HEALTHY" | "CRITICAL_FAILURE"
    checks: Dict[str, bool]
    timestamp: str
    metrics: Dict[str, Any] | None = None

    def is_healthy(self) -> bool:
        return self.status == "HEALTHY"


def verify_integrity(
    modules_dir: str | Path = "./modules",
    cache_dir: str | Path = "./memory/local",
) -> DiagnosticReport:
    """
    Run pre-flight checks. Returns a DiagnosticReport.

    Checks:
        - modules_dir exists and contains at least one module
        - cache_dir is writable (or can be created)
    """
    checks: Dict[str, bool] = {}
    metrics: Dict[str, Any] = {}

    # Check 1: modules directory
    def check_modules() -> bool:
        modules_path = Path(modules_dir)
        return modules_path.exists() and any(modules_path.glob("*/README.md"))

    # Check 2: cache directory writable
    def check_cache() -> bool:
        cache_path = Path(cache_dir)
        try:
            cache_path.mkdir(parents=True, exist_ok=True)
            test_file = cache_path / ".tessera_diag_test"
            test_file.write_text("ok")
            test_file.unlink()
            return True
        except OSError:
            return False

    # Execute checks with telemetry
    modules_passed, modules_duration = execute_check_with_telemetry(check_modules, "modules_dir")
    cache_passed, cache_duration = execute_check_with_telemetry(check_cache, "cache_writable")

    checks["modules_dir"] = modules_passed
    checks["cache_writable"] = cache_passed

    metrics["modules_dir_duration_ms"] = modules_duration
    metrics["cache_writable_duration_ms"] = cache_duration

    is_healthy = all(checks.values())
    
    return DiagnosticReport(
        status="HEALTHY" if is_healthy else "CRITICAL_FAILURE",
        checks=checks,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        metrics=metrics,
    )


def run_system_diagnostics(
    modules_dir: str | Path = "./modules",
    cache_dir: str | Path = "./memory/local",
) -> Dict[str, Any]:
    """
    Executes the full diagnostic suite for the Tessera Enterprise system.
    Validates environment, memory, and registry integrity with telemetry.
    """
    logger.info("[DIAGNOSTIC] Starting Tessera Enterprise integrity check...")
    report = verify_integrity(modules_dir, cache_dir)
    summary = summarize_diagnostic_results(report.checks)
    
    return {
        'status': report.status,
        'timestamp': report.timestamp,
        'checks': report.checks,
        'summary': summary,
        'metrics': report.metrics
    }
