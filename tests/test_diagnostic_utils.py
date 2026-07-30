"""
DIAGNOSTIC UTILITIES FOR TEST SUITES
Role: Provides standardized diagnostic hooks for test environments.
Integration: Interfaces with the main diagnostic_engine.py and diagnostic_registry.py.

This module serves as the primary test-time gatekeeper, ensuring that all 
unit and integration tests adhere to the system's diagnostic integrity standards.
"""

import datetime
from typing import Dict, Any
from tests.diagnostic_registry import get_test_registry_checks

def run_test_diagnostics(context: str) -> Dict[str, Any]:
    """
    Standardized diagnostic hook for test suites.
    Executes registry-defined checks and returns a structured diagnostic report.
    """
    try:
        checks = get_test_registry_checks()
        
        return {
            'status': 'HEALTHY',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'context': context,
            'checks': checks
        }
    except Exception as e:
        return {
            'status': 'ERROR',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'context': context,
            'error': str(e)
        }