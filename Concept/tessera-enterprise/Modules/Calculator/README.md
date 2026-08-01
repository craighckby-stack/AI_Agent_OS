# Module: calculator

name: calculator
purpose: Evaluates mathematical expressions deterministically using Python's ast module. Returns exact numerical results — no LLM hallucination, no approximation. Supports +, -, *, /, **, parentheses, and standard math functions.
cluster_key: request

## Description

This module does **real arithmetic** — the LLM cannot reliably do math.
It parses the user's request, extracts a mathematical expression, and
evaluates it using Python's `ast` module with a restricted safe-eval.

The output is the exact numerical result, formatted appropriately:
- Integers stay integers (e.g. `4` not `4.0`)
- Floats preserve precision (e.g. `3.141592653589793`)
- Division results are floats

## Diagnostic Integrity

This module is integrated with the **Enterprise Diagnostic Engine**. Before execution, the system performs a pre-flight check to validate:
1. The integrity of the AST whitelist.
2. The availability of the math function environment.
3. The readiness of the evaluation sandbox.

Modules must implement the `validate_calculator_environment` hook to ensure compatibility with the kernel's diagnostic lifecycle.

## Cluster key

`request` — each unique expression gets its own cache slot. Repeat
queries for the same expression return instantly.

## Inputs

The mathematical expression is extracted from the request via regex.
Supported patterns:
- "what is 2+2"
- "calculate 15 * 23"
- "compute (3 + 4) ** 2"
- "evaluate sqrt(16) + pi"

## Outputs

Plain text: the numerical result, or an error message.

## Safety

The evaluator uses `ast.parse` and walks the AST, only allowing:
- Numbers (int, float)
- Binary operators: +, -, *, /, **, %, //
- Unary operators: -, +
- Parentheses
- Calls to a whitelist of math functions: sqrt, sin, cos, tan, log, ln,
  exp, abs, round, floor, ceil, pi, e

No `__import__`, no `eval`, no attribute access, no name lookup outside
the whitelist. This is safe even on untrusted input.

## Example

```bash
tessera "what is 2+2"
# Result: 4

tessera "calculate 15 * 23"
# Result: 345

tessera "compute sqrt(144) + pi"
# Result: 15.141592653589793
```