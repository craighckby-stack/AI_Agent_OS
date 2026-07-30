#!/usr/bin/env bash
# ==============================================================================
# LICENSE DIAGNOSTIC UTILITIES
# Role: Standardized reporting and diagnostic hooks for compliance scripts.
# Integration: Connects to license-diagnostic-registry.sh for state validation.
# ==============================================================================

# Import registry for complex diagnostic orchestration
# shellcheck source=scripts/license-diagnostic-registry.sh
source "$(dirname "$0")/license-diagnostic-registry.sh"

log_diagnostic() {
    echo "[DIAGNOSTIC] $(date -u +"%Y-%m-%dT%H:%M:%SZ"): $1"
}

report_success() {
    echo "[SUCCESS] $(date -u +"%Y-%m-%dT%H:%M:%SZ"): $1"
}

report_failure() {
    echo "[FAILURE] $(date -u +"%Y-%m-%dT%H:%M:%SZ"): $1" >&2
}

# Execute system-wide compliance check via delegated registry
run_license_compliance_check() {
    log_diagnostic "Initiating license compliance suite..."
    if perform_license_integrity_check; then
        report_success "License integrity verified."
        return 0
    else
        report_failure "License integrity check failed."
        return 1
    fi
}