"""
DIAGNOSTIC REGISTRY FOR TEST SUITES
Role: Centralized registry for test-specific diagnostic checks.
Integration: Called by tests/test_diagnostic_utils.py and system health monitors.

This registry acts as the primary source of truth for test-environment integrity,
ensuring all critical test dependencies are verified before execution.
"""

from typing import Dict, Any, Callable
from tests.diagnostic_registry_utils import validate_env, validate_persistence, validate_registry

# System Health Versioning
SYSTEM_HEALTH_VERSION = "1.0.0"

# Registry mapping for dynamic diagnostic execution
REGISTERED_TEST_CHECKS: Dict[str, Callable[[], bool]] = {
    'env_loader': validate_env,
    'mock_persistence': validate_persistence,
    'registry_integrity': validate_registry
}

def get_test_registry_checks() -> Dict[str, Callable[[], bool]]:
    """
    Returns the current set of diagnostic check functions for test environments.
    """
    return REGISTERED_TEST_CHECKS

def execute_test_diagnostic(check_name: str) -> bool:
    """
    Executes a specific diagnostic check by name from the registry.
    """
    check_func = REGISTERED_TEST_CHECKS.get(check_name)
    if check_func:
        return check_func()
    return False