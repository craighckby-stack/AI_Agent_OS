#!/usr/bin/env python3
"""
TESSERA — SEMANTIC RADIUS BENCHMARK
Role: Measures intent-clustered caching efficiency across diverse phrasings.
Integration: Aligned with Tessera Diagnostic Engine for telemetry and system health validation.

Run: python3 -m benchmarks.semantic_radius
"""
import sys
import time
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tessera.config import TesseraConfig
from tessera.kernel import Kernel
from tessera.diagnostic_engine import run_system_diagnostics

# 10 different phrasings of "analyze this image"
SEMANTIC_PHRASINGS = [
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
]

def main():
    # 1. Pre-execution Diagnostic Integrity Check
    diag_report = run_system_diagnostics()
    if diag_report.get('status') != 'HEALTHY':
        print(f"[CRITICAL] Benchmark aborted: System health degraded: {diag_report.get('status')}")
        sys.exit(1)

    print("=" * 78)
    print("  TESSERA SEMANTIC RADIUS BENCHMARK [DIAGNOSTIC-AWARE]")
    print("=" * 78)
    
    repo_root = Path(__file__).parent.parent
    config = TesseraConfig.from_env()
    config.modules_dir = str(repo_root / "modules")
    config.cache_dir = str(repo_root / "memory" / "local")

    kernel = Kernel(config=config)
    kernel.cache.clear()

    cache_hits = 0
    total_elapsed_ms = 0

    print(f"\n{'#':<4} {'Phrasing':<50} {'Result':<8} {'Latency':<10}")
    print("-" * 76)

    for i, phrasing in enumerate(SEMANTIC_PHRASINGS, 1):
        start = time.perf_counter()
        result = kernel.run(phrasing)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        if result.cache_hit:
            cache_hits += 1
            status = "HIT"
        else:
            status = "MISS"
            
        total_elapsed_ms += elapsed_ms
        print(f"{i:<4} {phrasing[:50]:<50} {status:<8} {elapsed_ms:>7.1f}ms")

    print(f"\n{'=' * 78}")
    print(f"  BENCHMARK RESULTS")
    print(f"{'=' * 78}")
    print(f"  Cache hits:    {cache_hits}/{len(SEMANTIC_PHRASINGS)} ({cache_hits / len(SEMANTIC_PHRASINGS) * 100:.0f}%)")
    print(f"  Avg latency:   {total_elapsed_ms / len(SEMANTIC_PHRASINGS):.1f}ms")
    
    if cache_hits >= len(SEMANTIC_PHRASINGS) - 1:
        print(f"\n  ✅ PERFECT — intent clustering verified.")
    else:
        print(f"\n  ❌ FAILED — intent clustering threshold not met.")

if __name__ == "__main__":
    main()