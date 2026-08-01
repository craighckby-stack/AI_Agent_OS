#!/bin/bash
# diagnostic_hook.sh — Pre-flight validation for General_qa module.
# Ensures environment integrity before execution.

perform_pre_flight_check() {
    # Check Python availability
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[diagnostic] Error: python3 not found." >&2
        return 1
    fi

    # Check Cache directory permissions
    if [ ! -w "." ]; then
        echo "[diagnostic] Error: Module directory not writable." >&2
        return 1
    fi

    # Check API Key availability
    if [ -z "$OPENAI_API_KEY" ] && ! command -v z-ai >/dev/null 2>&1; then
        echo "[diagnostic] Error: No LLM provider configured (z-ai or OPENAI_API_KEY)." >&2
        return 1
    fi

    return 0
}