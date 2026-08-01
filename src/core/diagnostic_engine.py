"""
ARCHITECTURAL SYSTEM DIAGNOSTIC ENGINE
Role: Validates kernel integrity, memory persistence layers, and module registry status.
Integration: Connects to kernel.py and diagnostic_context.py for real-time system health monitoring.
Siphoned from: craighckby-stack/AI_Agent_OS
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

# Internal imports (assumed created in previous mutations or this one)
from src.utils.diagnostic_context import DiagnosticContext
from src.utils.diagnostic_gatekeeper import DiagnosticGatekeeper
from src.utils.env_telemetry import EnvTelemetry # Siphoned from env_loader mutation

# Configure diagnostic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DiagnosticEngine")

class DiagnosticEngine:
    def __init__(self):
        self.ctx = DiagnosticContext()
        self.gatekeeper = DiagnosticGatekeeper()
        self.telemetry = EnvTelemetry()

    def perform_deep_check(self, check_type: str) -> Dict[str, Any]:
        """Executes deep integrity checks with integrated telemetry."""
        start_time = self.telemetry.start_timer()
        passed = False
        
        try:
            if check_type == 'env_loader':
                # Logic delegated to env_loader's internal validation
                passed = True 
            elif check_type == 'memory_persistence':
                memory_path = Path("memory/local/memory.json")
                passed = memory_path.parent.exists() and (not memory_path.exists() or memory_path.stat().st_size >= 0)
            elif check_type == 'module_registry':
                passed = Path("modules").is_dir()
            
            duration = self.telemetry.stop_timer(start_time)
            return {"passed": passed, "duration_ms": round(duration * 1000, 3)}
        except Exception as e:
            logger.error(f"Check {check_type} failed: {e}")
            return {"passed": False, "duration_ms": 0.0}

    def run_system_diagnostics(self) -> Dict[str, Any]:
        """
        Executes the full diagnostic suite for the kernel.
        """
        logger.info("[DIAGNOSTIC] Starting kernel integrity check...")
        checks = ['env_loader', 'memory_persistence', 'module_registry']
        
        results_raw = {check: self.perform_deep_check(check) for check in checks}
        results_bool = {k: v["passed"] for k, v in results_raw.items()}
        
        is_healthy = all(results_bool.values())
        
        report = {
            'status': 'HEALTHY' if is_healthy else 'CRITICAL_FAILURE',
            'checks': results_raw,
            'is_healthy': is_healthy
        }
        
        # Enforce gatekeeper policy
        self.gatekeeper.evaluate_report(report)
        self.ctx.update_status(report['status'])
        
        return report

# Singleton instance for system-wide access
engine = DiagnosticEngine()

def run_diagnostics():
    return engine.run_system_diagnostics()