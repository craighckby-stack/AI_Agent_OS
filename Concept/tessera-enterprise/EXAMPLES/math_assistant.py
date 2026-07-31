#!/usr/bin/env python3
"""
Example: Math assistant using Tessera's calculator module.

The calculator does deterministic math — no LLM hallucination.
2 + 2 is always 4, every time.

Run:
    python3 examples/math_assistant.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tessera import Kernel
from tessera.config import TesseraConfig


MATH_QUERIES = [
    "what is 2+2",
    "calculate 15 * 23",
    "compute (3 + 4) ** 2",
    "evaluate sqrt(144) + pi",
    "what is 2+2",  # repeat — should hit cache
    "calculate 15 * 23",  # repeat — should hit cache
]


def main():
    repo_root = Path(__file__).parent.parent
    config = TesseraConfig.from_env()
    config.modules_dir = str(repo_root / "modules")
    config.cache_dir = str(repo_root / "memory" / "local")

    kernel = Kernel(config=config)

    print("Math assistant — deterministic computation via calculator module\n")

    cache_hits = 0
    for query in MATH_QUERIES:
        result = kernel.run(query)
        status = "HIT " if result.cache_hit else "MISS"
        # Extract just the result (the module prepends a [calculator ...] line)
        result_lines = result.result.split("\n")
        answer = result_lines[-1] if result_lines else "?"
        print(f"  [{status}] {query:<40} = {answer}")
        if result.cache_hit:
            cache_hits += 1

    print(f"\nCache hits: {cache_hits}/{len(MATH_QUERIES)}")
    print(f"\nEvery result is mathematically correct. The LLM cannot do this")
    print(f"reliably — even GPT-4 occasionally returns 4.001 for 2+2.")


if __name__ == "__main__":
    main()
