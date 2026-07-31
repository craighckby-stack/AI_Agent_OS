#!/usr/bin/env python3
"""
calculator/eval.py — Safe mathematical expression evaluator.

Extracts a math expression from a natural-language request and evaluates
it deterministically using Python's ast module.

Safety: only numbers, binary/unary operators, parentheses, and a
whitelist of math functions are allowed. No imports, no attribute
access, no name lookup outside the whitelist.
"""
import ast
import math
import re
import sys


# Whitelisted names (constants and functions)
SAFE_NAMES = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "ln": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "pow": pow,
    "min": min,
    "max": max,
}

# Whitelisted binary operators
SAFE_BINOPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
}

# Whitelisted unary operators
SAFE_UNARYOPS = {
    ast.UAdd: lambda a: +a,
    ast.USub: lambda a: -a,
}


def safe_eval(node):
    """Recursively evaluate an AST node, enforcing the whitelist."""
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Disallowed constant: {node.value!r}")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in SAFE_BINOPS:
            raise ValueError(f"Disallowed operator: {op_type.__name__}")
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        return SAFE_BINOPS[op_type](left, right)
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in SAFE_UNARYOPS:
            raise ValueError(f"Disallowed unary op: {op_type.__name__}")
        operand = safe_eval(node.operand)
        return SAFE_UNARYOPS[op_type](operand)
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct function calls are allowed")
        func_name = node.func.id
        if func_name not in SAFE_NAMES:
            raise ValueError(f"Disallowed function: {func_name}")
        args = [safe_eval(a) for a in node.args]
        return SAFE_NAMES[func_name](*args)
    if isinstance(node, ast.Name):
        if node.id not in SAFE_NAMES:
            raise ValueError(f"Disallowed name: {node.id}")
        return SAFE_NAMES[node.id]
    raise ValueError(f"Disallowed AST node: {type(node).__name__}")


def extract_expression(request: str) -> str:
    """Extract a math expression from a natural-language request.

    Strips common prefixes like 'what is', 'calculate', 'compute',
    'evaluate', 'solve'. Returns the remaining text.
    """
    # Lowercase for prefix matching
    lowered = request.lower().strip()

    # Strip common prefixes
    prefixes = [
        "what is ",
        "what's ",
        "calculate ",
        "compute ",
        "evaluate ",
        "solve ",
        "what is the value of ",
        "what is the result of ",
    ]
    for prefix in prefixes:
        if lowered.startswith(prefix):
            lowered = lowered[len(prefix):]
            break

    # Strip trailing punctuation
    lowered = lowered.rstrip("?.!")

    # If there's still natural language, try to extract just the math part.
    # Match anything that looks like an expression: digits, operators,
    # parens, function names, decimal points.
    expr_match = re.search(
        r"([\d\w\s\+\-\*/\(\)\.\%\^,]+(?:\*\*|//|sqrt|sin|cos|tan|log|ln|exp|abs|round|floor|ceil|pow|min|max|pi|e|tau)[\d\w\s\+\-\*/\(\)\.\%\^,]*)",
        lowered,
    )
    if expr_match:
        candidate = expr_match.group(1).strip()
        # Replace ^ with ** for convenience
        candidate = candidate.replace("^", "**")
        return candidate

    # Fall back to the whole stripped request
    return lowered.replace("^", "**")


def format_result(value) -> str:
    """Format the numerical result appropriately."""
    if isinstance(value, float):
        # If it's a whole number, show as int
        if value.is_integer():
            return str(int(value))
        # Otherwise show full precision
        return repr(value)
    return str(value)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 eval.py '<request>'", file=sys.stderr)
        sys.exit(1)

    request = sys.argv[1]
    expr = extract_expression(request)

    try:
        tree = ast.parse(expr, mode="eval")
        result = safe_eval(tree)
        print(format_result(result))
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError) as e:
        print(f"Error evaluating '{expr}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
