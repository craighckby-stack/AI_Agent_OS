"""
Tessera typed exceptions.

Each exception class represents a distinct failure mode so callers can
handle them granularly without parsing error strings.
"""

from __future__ import annotations


class TesseraError(Exception):
    """Base class for all Tessera exceptions."""


class CacheMiss(TesseraError):
    """Raised when a cache lookup misses. Usually not caught — the kernel
    handles misses internally and falls through to execution."""


class ModuleFailed(TesseraError):
    """Raised when a module execution fails (non-zero exit or timeout).

    Attributes:
        module_name: The name of the module that failed.
        message: The error output from the module.
    """

    def __init__(self, module_name: str, message: str) -> None:
        self.module_name = module_name
        self.message = message
        super().__init__(f"Module '{module_name}' failed: {message}")


class NoModuleMatched(TesseraError):
    """Raised when no module can be found to handle a request AND no
    default fallback module is configured."""


class KernelError(TesseraError):
    """Raised when the kernel itself encounters an internal error."""


class RouterError(TesseraError):
    """Raised when the LLM router fails to make a decision."""


class ConfigError(TesseraError):
    """Raised when configuration is invalid or incomplete."""
