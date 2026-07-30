#!/bin/bash
# ARCHITECTURAL DIAGNOSTIC UTILITY: sky_colour
# Role: Validates the integrity of the sky_colour module.
# Integration: Connects to the global diagnostic suite via diagnostic_registry.sh
# Version: 1.0.1-HEALTH-CHECK

# Source the delegated diagnostic registry and utils for modular validation logic
source "$(dirname "$0")/diagnostic_registry.sh"
source "$(dirname "$0")/diagnostic_utils.sh"

# Main diagnostic entry point
# Validates module dependencies and internal state integrity
perform_module_check() {
    local module_name="sky_colour"
    local system_health_version="1.0.0"
    
    echo "[DIAGNOSTIC] Initiating integrity check for: $module_name (v$system_health_version)"
    
    # Execute delegated integrity checks from diagnostic_utils.sh
    if validate_module_dependencies "$module_name" && validate_internal_state "$module_name"; then
        echo "[DIAGNOSTIC] $module_name: PASSED"
        return 0
    else
        echo "[DIAGNOSTIC] $module_name: FAILED"
        return 1
    fi
}

# Execute check if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    perform_module_check
fi