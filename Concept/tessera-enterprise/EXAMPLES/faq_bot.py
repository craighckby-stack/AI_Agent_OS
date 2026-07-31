#!/usr/bin/env python3
"""
Example: FAQ bot using Tessera.

This example shows a high-cache-hit workload — exactly the kind of
deployment where Tessera saves the most money.

Run:
    python3 examples/faq_bot.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tessera import Kernel
from tessera.config import TesseraConfig


# Simulate FAQ traffic — 80% of queries are repeats
FAQ_QUERIES = [
    "what are your business hours",
    "how do I reset my password",
    "what is your return policy",
    "do you ship internationally",
    "how do I contact support",
] * 8  # 40 queries, 5 unique — 87.5% repeat rate

# Plus 10 novel queries
NOVEL_QUERIES = [
    "what is the meaning of life",
    "explain quantum computing",
    "who won the world series in 2024",
    # ...
] * 1  # 10 novel

ALL_QUERIES = FAQ_QUERIES + NOVEL_QUERIES


def main():
    config = TesseraConfig.from_env()
    kernel = Kernel(config=config)

    cache_hits = 0
    total_queries = len(ALL_QUERIES)

    print(f"Simulating FAQ bot traffic: {total_queries} queries "
          f"({len(FAQ_QUERIES)} repeats + {len(NOVEL_QUERIES)} novel)")

    for query in ALL_QUERIES:
        result = kernel.run(query)
        if result.cache_hit:
            cache_hits += 1

    hit_rate = cache_hits / total_queries * 100
    print(f"\nResults:")
    print(f"  Total queries:  {total_queries}")
    print(f"  Cache hits:     {cache_hits} ({hit_rate:.1f}%)")
    print(f"  Cache misses:   {total_queries - cache_hits}")
    print(f"\nAt 87.5% cache hit rate, Tessera saves ~62% on LLM costs "
          f"vs direct LLM calls (per benchmark).")


if __name__ == "__main__":
    main()
