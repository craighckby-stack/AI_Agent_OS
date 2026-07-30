#!/usr/bin/env bash
# ==============================================================================
# LICENSE DIAGNOSTIC UTILITY
# Role: Provides standardized logging and diagnostic hooks for compliance scripts.
# ==============================================================================

log_diagnostic() {
    echo "[DIAGNOSTIC] $(date -u +"%Y-%m-%dT%H:%M:%SZ"): $1"
}

report_success() {
    echo "[SUCCESS] $(date -u +"%Y-%m-%dT%H:%M:%SZ"): $1"
}

report_failure() {
    echo "[CRITICAL_FAILURE] $(date -u +"%Y-%m-%dT%H:%M:%SZ"): $1" >&2
}