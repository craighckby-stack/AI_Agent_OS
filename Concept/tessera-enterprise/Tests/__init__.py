"""
ARCHITECTURAL TEST SUITE ENTRY POINT
Role: Orchestrates diagnostic test discovery and execution for the Tessera Enterprise ecosystem.
Integration: Connects to the Enterprise Diagnostic Engine to provide standardized test reporting.
Dependencies: tessera_test_registry, diagnostic_utils_core

This module serves as the root for all test-bench operations, ensuring that 
all diagnostic hooks are initialized and validated before execution.
"""

import logging
from typing import Dict, Callable, Any
from .tessera_test_registry import REGISTERED_TESTS

# Configure diagnostic logging for the test suite
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TesseraTestEngine")

def run_all_tests() -> Dict[str, Any]:
    """
    Executes the full suite of registered diagnostic tests.
    Aggregates results into a standardized report format.
    """
    logger.info("[TESTING] Initiating Tessera Enterprise diagnostic suite...")
    
    results = {}
    for test_name, test_func in REGISTERED_TESTS.items():
        try:
            logger.info(f"[TESTING] Running: {test_name}")
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"[TESTING] Fatal error in {test_name}: {e}")
            results[test_name] = {"passed": False, "error": str(e)}
            
    return results

__all__ = ['run_all_tests', 'REGISTERED_TESTS']