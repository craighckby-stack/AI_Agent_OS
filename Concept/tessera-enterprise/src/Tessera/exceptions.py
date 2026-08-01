"""
Tessera typed exceptions.

Each exception class represents a distinct failure mode so callers can
handle them granularly without parsing error strings.

Integration: Connects to diagnostic_engine.py to provide rich error telemetry.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from .exception_utils import get_diagnostic_context_snapshot

class TesseraError(Exception):
    """Base class for all Tessera exceptions with diagnostic metadata support."""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.context = context or get_diagnostic_context_snapshot()
        super().__init__(message)

class CacheMiss(TesseraError):
    """Raised when a cache lookup misses."""

class ModuleFailed(TesseraError):
    """Raised when a module execution fails (non-zero exit or timeout)."""
    def __init__(self, module_name: str, message: str) -> None:
        self.module_name = module_name
        self.message = message
        super().__init__(f"Module '{module_name}' failed: {message}")

class NoModuleMatched(TesseraError):
    """Raised when no module can be found to handle a request."""

class KernelError(TesseraError):
    """Raised when the kernel itself encounters an internal error."""

class RouterError(TesseraError):
    """Raised when the LLM router fails to make a decision."""

class ConfigError(TesseraError):
    """Raised when configuration is invalid or incomplete."""