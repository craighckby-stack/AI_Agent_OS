"""
ARCHITECTURAL SYSTEM DIAGNOSTIC ENGINE
Role: Validates kernel integrity, memory persistence layers, and module registry status.
Integration: Connects to AI_Agent_OS kernel for real-time system health monitoring.
"""

import datetime
import json
from diagnostic_utils import perform_deep_check

def run_system_diagnostics():
    """
    Executes the full diagnostic suite for the AI_Agent_OS kernel.
    Returns a structured health report.
    """
    print("[DIAGNOSTIC] Starting kernel integrity check...")
    
    try:
        # Execute core checks
        checks = ['env_loader', 'memory_persistence', 'module_registry']
        results = {check: perform_deep_check(check) for check in checks}
        
        # Aggregate status
        is_healthy = all(results.values())
        
        report = {
            'status': 'HEALTHY' if is_healthy else 'CRITICAL_FAILURE',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'checks': results,
            'version': '1.0.4-stable'
        }
        
        print(f"[DIAGNOSTIC] System status: {report['status']}")
        return report
        
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': str(e),
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
        }

if __name__ == "__main__":
    print(json.dumps(run_system_diagnostics(), indent=4))