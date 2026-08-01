"""
TEST REGISTRY
Role: Centralized registry for diagnostic test functions.
Integration: Imported by __init__.py to facilitate test discovery.
"""

from typing import Dict, Callable, Any

# Registry for diagnostic test functions
REGISTERED_TESTS: Dict[str, Callable[[], Any]] = {}

def register_test(name: str):
    """Decorator to register a test function."""
    def decorator(func: Callable[[], Any]):
        REGISTERED_TESTS[name] = func
        return func
    return decorator