#!/bin/bash
# TELEMETRY HELPER
# Role: Centralized logging and state management for General_qa module.

log_event() {
    local level=$1
    local message=$2
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] [general_qa $level] $message" >&2
}

cleanup_transient() {
    if [ -f "$1" ]; then
        rm -f "$1"
    fi
}