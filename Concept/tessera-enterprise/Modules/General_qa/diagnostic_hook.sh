#!/bin/bash
# diagnostic_hook.sh — Pre-flight integrity check for General_qa module.
# Role: Validates environment variables and module dependencies.

perform_pre_flight_check() {
    # Check for required environment variables
    if [ -z "${OPENAI_API_KEY:-}" ] && ! command -v z-ai >/dev/null 2>&1; then
        echo "[DIAGNOSTIC] Missing API_KEY or z-ai binary" >&2
        return 1
    fi

    # Check for python3 availability
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[DIAGNOSTIC] Python3 not found" >&2
        return 1
    fi

    return 0
}