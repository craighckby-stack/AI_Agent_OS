#!/bin/bash
# ARCHITECTURAL DIAGNOSTIC UTILITY: sky_colour
# Role: Validates the integrity of the sky_colour module.
# Integration: Connects to the global diagnostic suite via diagnostic_registry.sh
# Version: 1.1.0-DIAGNOSTIC-AWARE

# Source the delegated diagnostic registry and utils for modular validation logic
source "$(dirname "$0")/diagnostic_registry.sh"
source "$(dirname "$0")/diagnostic_utils.sh"
source "$(dirname "$0")/diagnostic_telemetry.sh"

# Main diagnostic entry point
# Validates module dependencies and internal state integrity with telemetry-rich reporting
perform_module_check() {
    local module_name="sky_colour"
    local system_health_version="1.1.0"
    
    echo "[DIAGNOSTIC] Initiating integrity check for: $module_name (v$system_health_version)"
    
    # Execute delegated integrity checks with telemetry capture
    local start_time=$(date +%s%N)
    
    if validate_module_dependencies "$module_name" && validate_internal_state "$module_name"; then
        local end_time=$(date +%s%N)
        generate_diagnostic_report "$module_name" "SUCCESS" "$start_time" "$end_time"
        echo "[DIAGNOSTIC] $module_name: PASSED"
        return 0
    else
        local end_time=$(date +%s%N)
        generate_diagnostic_report "$module_name" "FAILURE" "$start_time" "$end_time"
        echo "[DIAGNOSTIC] $module_name: FAILED"
        return 1
    fi
}

# Execute check if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    perform_module_check
fi