"""
CALCULATOR DIAGNOSTIC HOOKS
Role: Validates the calculator's AST environment and math function availability.
Integration: Called by the Tessera Enterprise Diagnostic Engine during system pre-flight.
"""

import ast
import math
from typing import Any, Dict, Final

__all__ = ["validate_calculator_environment"]

_TIMESTAMP_TAG: Final[str] = "SYSTEM_DIAGNOSTIC_V1"
_TEST_AST_EXPRESSION: Final[str] = "1 + 1"
_TEST_SQRT_VALUE: Final[float] = 144.0
_EXPECTED_SQRT_RESULT: Final[float] = 12.0


def validate_calculator_environment() -> Dict[str, Any]:
    """
    Performs a pre-flight check on the calculator's evaluation sandbox.
    Ensures math functions and AST parser are operational.
    """
    try:
        # Verify math library functionality
        if not math.isclose(math.sqrt(_TEST_SQRT_VALUE), _EXPECTED_SQRT_RESULT):
            raise ArithmeticError("Math module sqrt validation failed")

        # Verify AST parsing capability
        ast.parse(_TEST_AST_EXPRESSION, mode="eval")

        return {
            "status": "READY",
            "math_integrity": True,
            "ast_integrity": True,
            "timestamp": _TIMESTAMP_TAG,
        }
    except Exception as e:
        return {
            "status": "CRITICAL_FAILURE",
            "error": str(e),
            "math_integrity": False,
            "ast_integrity": False,
        }