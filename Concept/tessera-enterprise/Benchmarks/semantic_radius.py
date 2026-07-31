#!/usr/bin/env python3
"""
Tessera — Semantic Radius Benchmark
=====================================

Measures how many distinct phrasings of the same intent hit the same
cache slot. This is the benchmark that proves intent-clustered caching
works across phrasing diversity.

Run: python3 -m benchmarks.semantic_radius
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tessera.config import TesseraConfig
from tessera.kernel import Kernel


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
    print("=" * 78)
    print("  TESSERA SEMANTIC RADIUS BENCHMARK")
    print("=" * 78)
    print(f"\nTesting {len(SEMANTIC_PHRASINGS)} phrasings of the same intent")
    print("(all refer to sample.jpg — should share one cache slot)")

    # Make sure we're looking at the right modules dir
    repo_root = Path(__file__).parent.parent
    config = TesseraConfig.from_env()
    config.modules_dir = str(repo_root / "modules")
    config.cache_dir = str(repo_root / "memory" / "local")

    kernel = Kernel(config=config)

    # Clear any prior cache
    kernel.cache.clear()

    print(f"\nModules dir: {config.modules_dir}")
    print(f"Discovered modules: {kernel.registry.names()}")

    cache_hits = 0
    cache_misses = 0
    total_elapsed_ms = 0

    print(f"\n{'#':<4} {'Phrasing':<50} {'Result':<8} {'Latency':<10}")
    print("-" * 76)

    for i, phrasing in enumerate(SEMANTIC_PHRASINGS, 1):
        result = kernel.run(phrasing)
        if result.cache_hit:
            cache_hits += 1
            status = "HIT"
        else:
            cache_misses += 1
            status = "MISS"
        total_elapsed_ms += result.elapsed_s * 1000
        print(f"{i:<4} {phrasing[:50]:<50} {status:<8} {result.elapsed_s * 1000:>7.1f}ms")

    print(f"\n{'=' * 78}")
    print(f"  RESULTS")
    print(f"{'=' * 78}")
    print(f"  Cache hits:    {cache_hits}/{len(SEMANTIC_PHRASINGS)} "
          f"({cache_hits / len(SEMANTIC_PHRASINGS) * 100:.0f}%)")
    print(f"  Cache misses:  {cache_misses}")
    print(f"  Total latency: {total_elapsed_ms:.0f}ms")
    print(f"  Avg per query: {total_elapsed_ms / len(SEMANTIC_PHRASINGS):.1f}ms")

    if cache_hits == len(SEMANTIC_PHRASINGS) - 1:
        print(f"\n  ✅ PERFECT — all phrasings after the first hit the cache.")
    elif cache_hits > 0:
        print(f"\n  ⚠️  Partial — {cache_hits} hits but expected {len(SEMANTIC_PHRASINGS) - 1}.")
    else:
        print(f"\n  ❌ No cache hits — intent clustering not working.")


if __name__ == "__main__":
    main()
