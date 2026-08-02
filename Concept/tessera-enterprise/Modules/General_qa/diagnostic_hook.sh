#!/bin/bash
# diagnostic_hook.sh — Pre-flight integrity check for General_qa module.
# Role: Validates environment variables, system dependencies, and directory permissions.
# Integration: Connects to diagnostic_telemetry.py for structured reporting.

# Ensure we are in the module root
MODULE_ROOT="$(dirname "$(readlink -f "$0")")"
TELEMETRY_SCRIPT="$MODULE_ROOT/diagnostic_telemetry.py"

perform_pre_flight_check() {
    # 1. Check for required environment variables
    if [ -z "${OPENAI_API_KEY:-}" ] && ! command -v z-ai >/dev/null 2>&1; then
        python3 "$TELEMETRY_SCRIPT" "CRITICAL" "Missing API_KEY or z-ai binary"
        return 1
    fi

    # 2. Check for python3 availability
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[DIAGNOSTIC] Python3 not found" >&2
        return 1
    fi

    # 3. Validate module file existence
    if [ ! -f "$MODULE_ROOT/main.py" ]; then
        python3 "$TELEMETRY_SCRIPT" "ERROR" "main.py not found in module root"
        return 1
    fi

    # 4. Validate write permissions for logs/memory
    mkdir -p "$MODULE_ROOT/logs"
    if [ ! -w "$MODULE_ROOT/logs" ]; then
        python3 "$TELEMETRY_SCRIPT" "ERROR" "Logs directory not writable"
        return 1
    fi

    python3 "$TELEMETRY_SCRIPT" "HEALTHY" "General_qa environment validated"
    return 0
}

# Execute check
perform_pre_flight_check
exit $?