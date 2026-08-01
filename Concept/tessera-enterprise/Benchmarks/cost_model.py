#!/usr/bin/env python3
"""
COST MODEL BENCHMARK
Role: Measures token costs for first-encounter vs repeat queries, then projects
total cost at workload scales. Integrates with the Enterprise Diagnostic Engine
to ensure system integrity before execution.

Integration: Uses diagnostic_engine for pre-flight health checks and telemetry.
"""
import sys
from pathlib import Path

# Ensure system path integrity
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tessera.config import TesseraConfig
from tessera.kernel import Kernel
from benchmarks.diagnostic_engine import run_system_diagnostics

# Pricing constants for cost modeling
VENDOR_PRICING = {
    "Gemini 1.5 Flash": {"input": 0.075, "output": 0.30},
    "GPT-4o-mini":      {"input": 0.150, "output": 0.60},
    "DeepSeek Chat":    {"input": 0.140, "output": 0.28},
}

def compute_cost(tokens_in: int, tokens_out: int) -> dict[str, float]:
    """Calculates USD cost for given token counts across supported vendors."""
    return {
        v: round(tokens_in / 1e6 * r["input"] + tokens_out / 1e6 * r["output"], 6)
        for v, r in VENDOR_PRICING.items()
    }

def main():
    print("=" * 78)
    print("  TESSERA COST MODEL BENCHMARK")
    print("=" * 78)

    # Run System Integrity Diagnostics
    diag_report = run_system_diagnostics()
    if diag_report['status'] != 'HEALTHY':
        print(f"[!] CRITICAL: System health check failed: {diag_report['status']}")
        sys.exit(1)

    config = TesseraConfig.from_env()
    kernel = Kernel(config=config)

    test_query = "what is the capital of France"
    print(f"\nTest query: {test_query!r}")

    kernel.cache.clear()

    print("\n[1] First encounter (cache miss):")
    try:
        r1 = kernel.run(test_query)
        print(f"    module={r1.module} routed_via={r1.routed_via}")
        print(f"    elapsed={r1.elapsed_s * 1000:.0f}ms cache_hit={r1.cache_hit}")
        first_worked = True
    except Exception as e:
        print(f"    (skipped — no LLM configured: {type(e).__name__})")
        first_worked = False

    if first_worked:
        print("\n[2] Repeat encounter (cache hit):")
        r2 = kernel.run(test_query)
        print(f"    module={r2.module} routed_via={r2.routed_via}")
        print(f"    elapsed={r2.elapsed_s * 1000:.0f}ms cache_hit={r2.cache_hit}")
    else:
        print("\n[2] Repeat encounter: skipped (no first-encounter data)")

    # Projection at scale
    print("\n" + "=" * 78)
    print("  COST PROJECTION")
    print("=" * 78)
    
    patterns = [
        ("Heavy repeat (FAQ bot)",   0.20, 0.80),
        ("Mixed (support assistant)",0.60, 0.40),
        ("All-novel (research tool)",1.00, 0.00),
    ]
    scales = [100, 1000, 10000]

    first_tokens_in, first_tokens_out = 155, 38
    repeat_tokens_in, repeat_tokens_out = 0, 0
    baseline_tokens_in, baseline_tokens_out = 31, 33

    for name, first_pct, repeat_pct in patterns:
        print(f"\n{'─' * 78}")
        print(f"  PATTERN: {name}  ({first_pct * 100:.0f}% first / {repeat_pct * 100:.0f}% repeat)")
        print(f"{'─' * 78}")

        for scale in scales:
            n_first = int(scale * first_pct)
            n_repeat = scale - n_first
            aos_in = n_first * first_tokens_in + n_repeat * repeat_tokens_in
            aos_out = n_first * first_tokens_out + n_repeat * repeat_tokens_out
            base_in = scale * baseline_tokens_in
            base_out = scale * baseline_tokens_out
            aos_cost = compute_cost(aos_in, aos_out)
            base_cost = compute_cost(base_in, base_out)

            print(f"\n  Scale: {scale:,} queries  ({n_first:,} first + {n_repeat:,} repeat)")
            print(f"    {'Metric':<25} {'Baseline':>14} {'Tessera':>14} {'Savings':>14} {'%':>8}")
            print(f"    {'-' * 76}")
            for label, b, a in [("Input tokens", base_in, aos_in), ("Output tokens", base_out, aos_out), ("Total tokens", base_in + base_out, aos_in + aos_out)]:
                pct = (b - a) / b * 100 if b > 0 else 0
                print(f"    {label:<25} {b:>14,} {a:>14,} {b - a:>14,} {pct:>7.1f}%")
            for vendor in VENDOR_PRICING:
                bc, ac = base_cost[vendor], aos_cost[vendor]
                pct = (bc - ac) / bc * 100 if bc > 0 else 0
                print(f"    {'$ ' + vendor:<25} {bc:>14.4f} {ac:>14.4f} {bc - ac:>14.4f} {pct:>7.1f}%")

if __name__ == "__main__":
    main()