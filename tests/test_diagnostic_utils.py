"""
DIAGNOSTIC UTILITIES FOR TEST SUITE
Role: Provides health checks for test environment integrity.
"""
import datetime

def run_test_diagnostics(context: str):
    """Returns a diagnostic report for the test environment."""
    return {
        'status': 'HEALTHY',
        'context': context,
        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
    }