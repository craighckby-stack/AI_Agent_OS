"""
CALCULATOR MODULE DIAGNOSTIC HOOK
Role: Validates the integrity of the Calculator module environment.
Integration: Called by eval.py before processing any mathematical expressions.
Connects to: diagnostic_utils.py for telemetry and reporting standards.
"""

import math
from typing import Dict, Any
from .diagnostic_utils import execute_check_with_telemetry, format_diagnostic_report

def run_module_diagnostics() -> Dict[str, Any]:
    """
    Performs a comprehensive pre-flight check on the calculator module environment.
    Validates math library integrity and environment accessibility.
    """
    checks = {}

    # 1. Verify Math Library Integrity
    def check_math_lib() -> bool:
        required_funcs = ['sqrt', 'sin', 'cos', 'log', 'pow', 'pi']
        return all(hasattr(math, func) for func in required_funcs)

    passed, duration = execute_check_with_telemetry(check_math_lib, "math_lib_integrity")
    checks['math_lib_integrity'] = {
        'passed': passed,
        'duration_ms': duration,
        'message': 'Math library functions verified' if passed else 'Critical math functions missing'
    }

    # 2. Verify Environment Execution Context
    def check_env() -> bool:
        # Ensure floating point precision is within standard IEEE 754 expectations
        return (0.1 + 0.2) > 0.3 and (0.1 + 0.2) < 0.30000000000000005

    passed_env, duration_env = execute_check_with_telemetry(check_env, "env_precision")
    checks['env_precision'] = {
        'passed': passed_env,
        'duration_ms': duration_env,
        'message': 'Floating point precision within expected bounds' if passed_env else 'Precision drift detected'
    }

    # Determine overall status
    is_healthy = all(c['passed'] for c in checks.values())
    status = 'HEALTHY' if is_healthy else 'CRITICAL_FAILURE'

    return format_diagnostic_report(status, checks)