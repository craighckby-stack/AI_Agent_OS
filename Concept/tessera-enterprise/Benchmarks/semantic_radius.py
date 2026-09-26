#!/usr/bin/env python3
"""
TESSERA — SEMANTIC RADIUS BENCHMARK
Role: Measures intent-clustered caching efficiency across diverse phrasings.
Integration: Aligned with Tessera Diagnostic Engine for telemetry and system health validation.

Run: python3 -m benchmarks.semantic_radius
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Final

# Ensure source directory is added to sys.path if not already present
REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
SRC_PATH: Final[Path] = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from tessera.config import TesseraConfig
from tessera.diagnostic_engine import run_system_diagnostics
from tessera.kernel import Kernel

# 10 different phrasings of "analyze this image"
SEMANTIC_PHRASINGS: Final[tuple[str, ...]] = (
    "analyze this image sample.jpg",
    "what colors are in sample.jpg",
    "give me RGB stats for sample.jpg",
    "extract dominant colors from sample.jpg",
    "tell me about the pixels in sample.jpg",
    "compute color histogram for sample.jpg",
    "what is the brightness of sample.jpg",
    "describe the color palette of sample.jpg",
    "show me hue distribution of sample.jpg",
    "pixel analysis on sample.jpg please",
)


def main() -> None:
    """Execute the semantic radius benchmark and report caching metrics."""
    # 1. Pre-execution Diagnostic Integrity Check
    try:
        diag_report: dict[str, Any] = run_system_diagnostics()
    except Exception as exc:
        print(f"[CRITICAL] Diagnostic check failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if diag_report.get("status") != "HEALTHY":
        status_val: Any = diag_report.get("status")
        print(f"[CRITICAL] Benchmark aborted: System health degraded: {status_val}", file=sys.stderr)
        sys.exit(1)

    print("=" * 78)
    print("  TESSERA SEMANTIC RADIUS BENCHMARK [DIAGNOSTIC-AWARE]")
    print("=" * 78)

    try:
        config = TesseraConfig.from_env()
        config.modules_dir = str(REPO_ROOT / "modules")
        config.cache_dir = str(REPO_ROOT / "memory" / "local")

        kernel = Kernel(config=config)
        kernel.cache.clear()
    except Exception as exc:
        print(f"[CRITICAL] Kernel initialization failed: {exc}", file=sys.stderr)
        sys.exit(1)

    cache_hits: int = 0
    total_elapsed_ms: float = 0.0
    total_phrasings: int = len(SEMANTIC_PHRASINGS)

    print(f"\n{'#':<4} {'Phrasing':<50} {'Result':<8} {'Latency':<10}")
    print("-" * 76)

    for i, phrasing in enumerate(SEMANTIC_PHRASINGS, 1):
        start: float = time.perf_counter()
        try:
            result = kernel.run(phrasing)
            elapsed_ms: float = (time.perf_counter() - start) * 1000.0

            if getattr(result, "cache_hit", False):
                cache_hits += 1
                status = "HIT"
            else:
                status = "MISS"
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            status = "ERROR"
            print(f"{i:<4} {phrasing[:50]:<50} {status:<8} {elapsed_ms:>7.1f}ms ({exc})")
            continue

        total_elapsed_ms += elapsed_ms
        print(f"{i:<4} {phrasing[:50]:<50} {status:<8} {elapsed_ms:>7.1f}ms")

    print(f"\n{'=' * 78}")
    print("  BENCHMARK RESULTS")
    print(f"{'=' * 78}")

    if total_phrasings > 0:
        hit_percentage: float = (cache_hits / total_phrasings) * 100.0
        avg_latency: float = total_elapsed_ms / total_phrasings
        print(f"  Cache hits:    {cache_hits}/{total_phrasings} ({hit_percentage:.0f}%)")
        print(f"  Avg latency:   {avg_latency:.1f}ms")
    else:
        print("  No phrasings evaluated.")

    if cache_hits >= total_phrasings - 1 and total_phrasings > 0:
        print("\n  ✅ PERFECT — intent clustering verified.")
    else:
        print("\n  ❌ FAILED — intent clustering threshold not met.")


if __name__ == "__main__":
    main()