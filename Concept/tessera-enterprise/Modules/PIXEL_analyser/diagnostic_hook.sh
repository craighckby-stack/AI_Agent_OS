#!/bin/bash
# PIXEL_analyser Diagnostic Hook
# Validates environment for image processing modules.

run_preflight_diagnostics() {
    echo "[DIAGNOSTIC] Validating PIXEL_analyser environment..." >&2
    
    # Check Python availability
    if ! command -v python3 &> /dev/null; then
        echo "[ERROR] Python3 not found." >&2
        return 1
    fi

    # Check cache directory permissions
    CACHE_DIR="$(dirname "$0")/.cache"
    if [ ! -w "$CACHE_DIR" ] && [ -d "$CACHE_DIR" ]; then
        echo "[ERROR] Cache directory not writable." >&2
        return 1
    fi

    # Check for core dependencies (PIL/Numpy)
    if ! python3 -c "import PIL, numpy" &> /dev/null; then
        echo "[ERROR] Missing required image processing libraries (PIL/numpy)." >&2
        return 1
    fi

    echo "[DIAGNOSTIC] Environment healthy." >&2
    return 0
}