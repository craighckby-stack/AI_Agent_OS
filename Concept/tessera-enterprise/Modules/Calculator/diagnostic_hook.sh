#!/bin/bash
# diagnostic_hook.sh — Calculator Module Diagnostic Integrity
# Role: Validates module environment before execution.

run_module_diagnostics() {
    # Check for python3 availability
    if ! command -v python3 &> /dev/null; then
        echo "[diagnostic error] python3 not found" >&2
        return 1
    fi

    # Verify eval.py exists
    if [ ! -f "$MODULE_DIR/eval.py" ]; then
        echo "[diagnostic error] eval.py missing" >&2
        return 1
    fi

    # Verify cache directory is writable
    if [ ! -w "$MODULE_DIR" ]; then
        echo "[diagnostic error] Module directory not writable" >&2
        return 1
    fi

    return 0
}