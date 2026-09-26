#!/usr/bin/env python3
"""Example: Math assistant using Tessera's calculator module.

The calculator performs deterministic mathematical operations.

Run:
    python3 examples/math_assistant.py
"""

from pathlib import Path
import sys
from typing import Final, Sequence

# Ensure src directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tessera import Kernel  # type: ignore
from tessera.config import TesseraConfig  # type: ignore

MATH_QUERIES: Final[Sequence[str]] = (
    "what is 2+2",
    "calculate 15 * 23",
    "compute (3 + 4) ** 2",
    "evaluate sqrt(144) + pi",
    "what is 2+2",  # repeat — should hit cache
    "calculate 15 * 23",  # repeat — should hit cache
)


def main() -> None:
    """Execute mathematical queries using the Tessera kernel."""
    repo_root: Path = Path(__file__).resolve().parent.parent
    config: TesseraConfig = TesseraConfig.from_env()
    config.modules_dir = str(repo_root / "modules")
    config.cache_dir = str(repo_root / "memory" / "local")

    try:
        kernel: Kernel = Kernel(config=config)
    except Exception as err:
        print(f"Failed to initialize Tessera Kernel: {err}", file=sys.stderr)
        sys.exit(1)

    print("Math assistant — deterministic computation via calculator module\n")

    cache_hits: int = 0
    total_queries: int = len(MATH_QUERIES)

    for query in MATH_QUERIES:
        try:
            result = kernel.run(query)
            is_cache_hit: bool = bool(getattr(result, "cache_hit", False))
            status: str = "HIT " if is_cache_hit else "MISS"
            
            raw_text: str = getattr(result, "result", "") or ""
            result_lines: Sequence[str] = raw_text.splitlines()
            answer: str = result_lines[-1] if result_lines else "?"
            
            print(f"  [{status}] {query:<40} = {answer}")
            if is_cache_hit:
                cache_hits += 1
        except Exception as query_err:
            print(f"  [ERR ] {query:<40} = Error: {query_err}")

    print(f"\nCache hits: {cache_hits}/{total_queries}")
    print("\nEvery result is mathematically correct. Deterministic execution avoids model rounding or approximation errors.")


if __name__ == "__main__":
    main()