#!/usr/bin/env bash
# Diagnostic Utility for License Compliance

log_diagnostic() {
    echo "[DIAGNOSTIC] $(date -u +"%Y-%m-%dT%H:%M:%SZ"): $1"
}

report_success() {
    echo "[SUCCESS] $1"
}

report_failure() {
    echo "[CRITICAL_FAILURE] $1"
}