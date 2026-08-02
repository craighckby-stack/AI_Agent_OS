#!/bin/bash
# Diagnostic Utility Helpers for Calculator Module
# Provides standardized logging and environment verification routines.

LOG_PREFIX="[TESSERA-DIAGNOSTIC]"

log_info() {
    echo "$LOG_PREFIX [INFO] $1"
}

log_error() {
    echo "$LOG_PREFIX [ERROR] $1" >&2
}

verify_dependency() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Dependency missing: $1"
        return 1
    fi
    return 0
}

check_write_access() {
    if [ ! -w "$1" ]; then
        log_error "Write access denied to: $1"
        return 1
    fi
    return 0
}