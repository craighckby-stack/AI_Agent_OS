#!/usr/bin/env bash
# ==============================================================================
# LICENSE DIAGNOSTIC UTILS
# Role: Provides granular validation logic for license compliance.
# Integration: Called by license-diagnostic-registry.sh.
# System Health Version: 1.0.4
# ==============================================================================

# Import diagnostic logging utilities
source "$(dirname "$0")/diagnostic-logger.sh" 2>/dev/null || true

SYSTEM_HEALTH_VERSION="1.0.4"

# Validates source files for required copyright headers
perform_header_verification() {
    log_info "[DIAGNOSTIC] Initiating header verification..."
    local target_files=$(find . -name "*.ts" -o -name "*.py" -o -name "*.sh")
    
    for file in $target_files; do
        if ! grep -q "Copyright" "$file"; then
            log_warn "[DIAGNOSTIC] Missing license header in: $file"
            return 1
        fi
    done
    
    log_info "[DIAGNOSTIC] Header verification passed."
    return 0
}

# Validates the integrity of external license manifests
perform_dependency_audit() {
    log_info "[DIAGNOSTIC] Auditing license manifests..."
    if [ -f "LICENSE" ] || [ -f "LICENSE.md" ]; then
        return 0
    else
        log_error "[DIAGNOSTIC] Critical: No license manifest found."
        return 1
    fi
}

# Main entry point for diagnostic execution
run_license_diagnostics() {
    local status=0
    perform_header_verification || status=1
    perform_dependency_audit || status=1
    return $status
}