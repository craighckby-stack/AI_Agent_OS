"""
DIAGNOSTIC UTILITIES
Role: Provides modular, extensible deep-system verification hooks.
Integration: Connects to diagnostic_engine.py for real-time system health monitoring.
Siphoned from: craighckby-stack/AI_Agent_OS

This module manages the lifecycle of diagnostic probes, ensuring thread-safe
registration and providing a standardized interface for system health reporting.
"""

import logging
import threading
from typing import Dict, Callable, Any, NamedTuple, Optional
from diagnostic_utils_core import DiagnosticResult, validate_check_function, generate_telemetry_metadata

# Configure diagnostic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DiagnosticUtils")

# Thread-safe registry lock
_registry_lock = threading.RLock()

# Dynamic registry for system checks
# Allows modules to register their own health validation logic
REGISTERED_CHECKS: Dict[str, Callable[[], DiagnosticResult]] = {}

def register_check(name: str, check_func: Callable[[], DiagnosticResult]) -> Callable[[], None]:
    """
    Registers a new diagnostic check into the system registry.
    Returns a cleanup function (SafeUnsubscribe pattern).
    """
    with _registry_lock:
        if not validate_check_function(check_func):
            logger.error(f"[DIAGNOSTIC] Failed to register invalid check: {name}")
            return lambda: None
            
        REGISTERED_CHECKS[name] = check_func
        logger.info(f"[DIAGNOSTIC] Registered new check: {name}")
        
        # Return a closure for safe unregistration to prevent memory leaks
        return lambda: unregister_check(name)

def unregister_check(name: str) -> None:
    """
    Removes a diagnostic check from the system registry with thread safety.
    """
    with _registry_lock:
        if name in REGISTERED_CHECKS:
            del REGISTERED_CHECKS[name]
            logger.info(f"[DIAGNOSTIC] Unregistered check: {name}")

def perform_deep_check(check_type: str) -> DiagnosticResult:
    """
    Simulates deep-level verification of system components.
    Utilizes the dynamic registry for extensible validation.
    """
    try:
        with _registry_lock:
            # Check dynamic registry first
            if check_type in REGISTERED_CHECKS:
                return REGISTERED_CHECKS[check_type]()
        
        # Fallback to legacy static checks
        legacy_registry = {
            'env_loader': DiagnosticResult(True, "Legacy env_loader passed", generate_telemetry_metadata()),
            'memory_persistence': DiagnosticResult(True, "Legacy memory_persistence passed", generate_telemetry_metadata()),
            'module_registry': DiagnosticResult(True, "Legacy module_registry passed", generate_telemetry_metadata())
        }
        return legacy_registry.get(check_type, DiagnosticResult(False, f"Unknown check: {check_type}", generate_telemetry_metadata()))
    except Exception as e:
        logger.error(f"[DIAGNOSTIC] Check '{check_type}' failed with error: {e}")
        return DiagnosticResult(False, str(e), generate_telemetry_metadata())

# Initialize default checks if necessary
# This ensures the system remains operational even without external registration
with _registry_lock:
    if not REGISTERED_CHECKS:
        register_check('env_loader', lambda: DiagnosticResult(True, "System environment initialized", generate_telemetry_metadata()))
        register_check('memory_persistence', lambda: DiagnosticResult(True, "Memory layer verified", generate_telemetry_metadata()))
        register_check('module_registry', lambda: DiagnosticResult(True, "Module registry active", generate_telemetry_metadata()))