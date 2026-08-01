"""
BENCHMARK REGISTRY
Role: Centralized registry for all Tessera performance benchmarks.
"""

from typing import Dict, Callable

# Placeholder for future benchmark implementations
REGISTERED_BENCHMARKS: Dict[str, Callable] = {}

def register_benchmark(name: str):
    def decorator(func: Callable):
        REGISTERED_BENCHMARKS[name] = func
        return func
    return decorator