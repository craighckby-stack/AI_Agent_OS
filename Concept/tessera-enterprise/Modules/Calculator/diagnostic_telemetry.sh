#!/bin/bash
# diagnostic_telemetry.sh
# Role: Centralized logging and telemetry utility for the Calculator module.

log_info() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%SZ')] [INFO] $1" >&2
}

log_error() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%SZ')] [ERROR] $1" >&2
}

cleanup_transient_state() {
    unset REQ_NORM CACHE_KEY CACHE_FILE RESULT MODULE_DIR
}

verify_python_env() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 environment not found."
        return 1
    fi
    return 0
}