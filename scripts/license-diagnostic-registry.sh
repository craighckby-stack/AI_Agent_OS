#!/usr/bin/env bash
# ==============================================================================
# LICENSE DIAGNOSTIC REGISTRY
# Role: Orchestrates complex validation logic for license compliance.
# Integration: Acts as a primary registry for license integrity checks.
# System Health Version: 1.0.0-DIAGNOSTIC-AWARE
# ==============================================================================

# Import auxiliary diagnostic utilities
if [ -f "$(dirname "$0")/license-diagnostic-utils.sh" ]; then
    source "$(dirname "$0")/license-diagnostic-utils.sh"
fi

# Import global telemetry utilities
if [ -f "$(dirname "$0")/diagnostic-telemetry.sh" ]; then
    source "$(dirname "$0")/diagnostic-telemetry.sh"
fi

# Registry of license checks
declare -A REGISTERED_LICENSE_CHECKS

# Register standard integrity checks
REGISTERED_LICENSE_CHECKS["file_presence"]="perform_license_integrity_check"
REGISTERED_LICENSE_CHECKS["header_validation"]="perform_header_verification"

# Execute registered license diagnostics with telemetry
run_license_diagnostics() {
    local start_time=$(date +%s%N)
    local results=()
    local all_passed=0

    log_json "INFO" "Starting license integrity registry check..."
    
    for check_name in "${!REGISTERED_LICENSE_CHECKS[@]}"; do
        local check_func=${REGISTERED_LICENSE_CHECKS[$check_name]}
        if command -v "$check_func" >/dev/null 2>&1; then
            $check_func
            local status=$?
            if [ $status -ne 0 ]; then
                log_json "ERROR" "License check '$check_name' failed."
                all_passed=1
            fi
        else
            log_json "WARN" "Check function '$check_func' not found."
        fi
    done

    local end_time=$(date +%s%N)
    local duration_ms=$(( (end_time - start_time) / 1000000 ))

    # Generate final diagnostic report
    local report_status="HEALTHY"
    [ $all_passed -ne 0 ] && report_status="CRITICAL_FAILURE"
    
    log_json "DIAGNOSTIC_REPORT" "{\"status\": \"$report_status\", \"duration_ms\": $duration_ms, \"registry\": \"license_diagnostic_registry\"}"

    return $all_passed
}

# Legacy support for direct calls
perform_license_integrity_check() {
    local required_files=("LICENSE" "NOTICE")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_json "ERROR" "Missing mandatory file: $file"
            return 1
        fi
    done
    return 0
}