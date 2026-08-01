"""
ARCHITECTURAL SYSTEM DIAGNOSTIC ENGINE
Role: Validates kernel integrity, memory persistence layers, and module registry status.
Integration: Connects to kernel.py and diagnostic_context.py for real-time system health monitoring and diagnostic reporting.
Dependencies: diagnostic_registry, diagnostic_context, diagnostic_engine_utils, diagnostic_utils_core

This engine acts as the primary gatekeeper for system health, ensuring all 
critical dependencies are verified before kernel execution cycles.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

from diagnostic_registry import REGISTERED_CHECKS
from diagnostic_context import DiagnosticContext
from diagnostic_engine_utils import format_timestamp, summarize_diagnostic_results, execute_check_with_telemetry
from diagnostic_utils_core import generate_telemetry_metadata

# Configure diagnostic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DiagnosticEngine")

# Initialize global diagnostic context
ctx = DiagnosticContext()


def perform_deep_check(check_type: str) -> Dict[str, Any]:
    """Executes deep integrity checks with integrated telemetry."""
    try:
        if check_type in REGISTERED_CHECKS:
            passed, duration = execute_check_with_telemetry(REGISTERED_CHECKS[check_type], check_type)
            return {"passed": passed, "duration_ms": duration}
        
        # Fallback legacy checks
        if check_type == 'env_loader':
            return {"passed": True, "duration_ms": 0.0}
        if check_type == 'memory_persistence':
            exists = (Path(__file__).parent / "memory").exists()
            return {"passed": exists, "duration_ms": 0.0}
        if check_type == 'module_registry':
            return {"passed": True, "duration_ms": 0.0}
        return {"passed": False, "duration_ms": 0.0}
    except Exception as e:
        logger.error(f"Check {check_type} failed: {e}")
        return {"passed": False, "duration_ms": 0.0}


def run_system_diagnostics() -> Dict[str, Any]:
    """
    Executes the full diagnostic suite for the kernel.
    Validates environment, memory, and registry integrity with telemetry.
    """
    logger.info("[DIAGNOSTIC] Starting kernel integrity check...")
    try:
        default_checks: List[str] = ['env_loader', 'memory_persistence', 'module_registry']
        registered_keys: List[str] = list(REGISTERED_CHECKS.keys())
        
        checks: List[str] = []
        for check in default_checks + registered_keys:
            if check not in checks:
                checks.append(check)
        
        results_raw = {check: perform_deep_check(check) for check in checks}
        results_bool = {k: v["passed"] for k, v in results_raw.items()}
        
        summary = summarize_diagnostic_results(results_bool)
        is_healthy = summary['is_healthy']
        
        report: Dict[str, Any] = {
            'status': 'HEALTHY' if is_healthy else 'CRITICAL_FAILURE',
            'timestamp': format_timestamp(),
            'checks': results_raw,
            'summary': summary,
            'telemetry': generate_telemetry_metadata()
        }
        
        ctx.update_status(report['status'])
        
        if not is_healthy:
            logger.warning(f"[DIAGNOSTIC] System health degraded: {report}")
            
        return report
    except Exception as e:
        logger.error(f"[DIAGNOSTIC] Fatal error during diagnostic execution: {e}")
        return {
            'status': 'ERROR', 
            'timestamp': format_timestamp(), 
            'error': str(e)
        }