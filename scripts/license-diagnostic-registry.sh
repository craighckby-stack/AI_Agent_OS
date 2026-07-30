#!/usr/bin/env bash
# ==============================================================================
# LICENSE DIAGNOSTIC REGISTRY
# Role: Orchestrates complex validation logic for license compliance.
# Integration: Acts as a primary registry for license integrity checks.
# System Health Version: 1.0.0
# ==============================================================================

# Import auxiliary diagnostic utilities
if [ -f "$(dirname "$0")/license-diagnostic-utils.sh" ]; then
    source "$(dirname "$0")/license-diagnostic-utils.sh"
fi

# Registry of license checks
declare -A REGISTERED_LICENSE_CHECKS

# Register standard integrity checks
REGISTERED_LICENSE_CHECKS["file_presence"]="perform_license_integrity_check"
REGISTERED_LICENSE_CHECKS["header_validation"]="perform_header_verification"

# Execute registered license diagnostics
run_license_diagnostics() {
    echo "[DIAGNOSTIC] Starting license integrity registry check..."
    
    local all_passed=0
    for check_name in "${!REGISTERED_LICENSE_CHECKS[@]}"; do
        local check_func=${REGISTERED_LICENSE_CHECKS[$check_name]}
        if command -v "$check_func" >/dev/null 2>&1; then
            $check_func
            if [ $? -ne 0 ]; then
                echo "[ERROR] License check '$check_name' failed."
                all_passed=1
            fi
        else
            echo "[WARN] Check function '$check_func' not found."
        fi
    done

    return $all_passed
}

# Legacy support for direct calls
perform_license_integrity_check() {
    local required_files=("LICENSE" "NOTICE")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "[ERROR] Missing mandatory file: $file" >&2
            return 1
        fi
    done
    return 0
}