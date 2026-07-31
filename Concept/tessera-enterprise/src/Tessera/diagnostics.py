"""
Tessera diagnostics — fail-fast health checks.

The kernel calls verify_integrity() before processing any request. If
any critical check fails, the kernel refuses to start. This prevents
running in a corrupted state.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger("tessera.diagnostics")


@dataclass
class DiagnosticReport:
    """Result of a diagnostic run."""

    status: str  # "HEALTHY" | "CRITICAL_FAILURE"
    checks: Dict[str, bool]
    timestamp: str

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
    import time
    checks: Dict[str, bool] = {}

    # Check 1: modules directory
    modules_path = Path(modules_dir)
    checks["modules_dir"] = modules_path.exists() and any(modules_path.glob("*/README.md"))

    # Check 2: cache directory writable
    cache_path = Path(cache_dir)
    try:
        cache_path.mkdir(parents=True, exist_ok=True)
        test_file = cache_path / ".tessera_diag_test"
        test_file.write_text("ok")
        test_file.unlink()
        checks["cache_writable"] = True
    except OSError:
        checks["cache_writable"] = False

    is_healthy = all(checks.values())
    return DiagnosticReport(
        status="HEALTHY" if is_healthy else "CRITICAL_FAILURE",
        checks=checks,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
