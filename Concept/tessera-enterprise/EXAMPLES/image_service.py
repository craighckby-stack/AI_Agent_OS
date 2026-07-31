#!/usr/bin/env python3
"""
Example: Image analysis service using Tessera.

This example shows a real-computation workload — Tessera's strongest
use case. The pixel_analyzer module does work the LLM literally cannot.

Run:
    python3 examples/image_service.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tessera import Kernel
from tessera.config import TesseraConfig


# Simulate image-analysis traffic — same image, many phrasings
QUERIES = [
    "analyze this image sample.jpg",
    "what colors are in sample.jpg",
    "give me RGB stats for sample.jpg",
    "extract dominant colors from sample.jpg",
    "tell me about the pixels in sample.jpg",
    "compute color histogram for sample.jpg",
    "what is the brightness of sample.jpg",
    "describe the color palette of sample.jpg",
]


def main():
    # Point at the repo's modules dir
    repo_root = Path(__file__).parent.parent
    config = TesseraConfig.from_env()
    config.modules_dir = str(repo_root / "modules")
    config.cache_dir = str(repo_root / "memory" / "local")

    kernel = Kernel(config=config)
    kernel.cache.clear()  # start fresh

    print(f"Simulating image analysis: {len(QUERIES)} phrasings, same image")
    print(f"(pixel_analyzer uses cluster_key=extract:image — all phrasings")
    print(f" should share one cache slot)\n")

    cache_hits = 0
    for query in QUERIES:
        result = kernel.run(query)
        status = "HIT" if result.cache_hit else "MISS"
        print(f"  [{status}] {query}")
        if result.cache_hit:
            cache_hits += 1

    print(f"\nResults:")
    print(f"  Cache hits: {cache_hits}/{len(QUERIES)}")
    print(f"  LLM calls saved: {cache_hits} (each cache hit = 0 tokens)")
    print(f"\nThe direct LLM cannot access pixel data — its output would be")
    print(f"hallucinated. Tessera produces real numerical analysis from")
    print(f"actual pixel values, AND costs less.")


if __name__ == "__main__":
    main()
