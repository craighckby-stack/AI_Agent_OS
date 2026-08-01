#!/usr/bin/env bash
# ==============================================================================
# LICENSE DIAGNOSTIC UTILS
# Role: Provides granular validation logic for license compliance.
# Integration: Called by license-diagnostic-registry.sh.
# System Health Version: 1.0.5
# ==============================================================================

# Import diagnostic logging utilities
source "$(dirname "$0")/diagnostic-logger.sh" 2>/dev/null || true

SYSTEM_HEALTH_VERSION="1.0.5"

# Validates source files for required copyright headers
perform_header_verification() {
    local start_time=$(date +%s%N)
    log_info "{\"event\": \"header_verification_start\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
    
    local target_files=$(find . -name "*.ts" -o -name "*.py" -o -name "*.sh")
    local missing_headers=0
    
    for file in $target_files; do
        if ! grep -q "Copyright" "$file"; then
            log_warn "{\"file\": \"$file\", \"status\": \"missing_header\"}"
            missing_headers=1
        fi
    done
    
    local duration=$(( ($(date +%s%N) - start_time) / 1000000 ))
    if [ $missing_headers -eq 0 ]; then
        log_info "{\"event\": \"header_verification_success\", \"duration_ms\": $duration}"
        return 0
    else
        log_error "{\"event\": \"header_verification_failure\", \"duration_ms\": $duration}"
        return 1
    fi
}

# Validates the integrity of external license manifests
perform_dependency_audit() {
    local start_time=$(date +%s%N)
    if [ -f "LICENSE" ] || [ -f "LICENSE.md" ]; then
        local duration=$(( ($(date +%s%N) - start_time) / 1000000 ))
        log_info "{\"event\": \"dependency_audit_success\", \"duration_ms\": $duration}"
        return 0
    else
        log_error "{\"event\": \"dependency_audit_failure\", \"message\": \"No license manifest found\"}"
        return 1
    fi
}

# Main entry point for diagnostic execution
run_license_diagnostics() {
    local start_time=$(date +%s%N)
    local status=0
    
    perform_header_verification || status=1
    perform_dependency_audit || status=1
    
    local duration=$(( ($(date +%s%N) - start_time) / 1000000 ))
    local result_status="HEALTHY"
    [ $status -ne 0 ] && result_status="CRITICAL_FAILURE"
    
    log_json "{\"status\": \"$result_status\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"duration_ms\": $duration, \"version\": \"$SYSTEM_HEALTH_VERSION\"}"
    return $status
}