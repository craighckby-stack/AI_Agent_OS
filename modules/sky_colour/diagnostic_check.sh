#!/bin/bash
# ARCHITECTURAL DIAGNOSTIC UTILITY: sky_colour
# Role: Validates the integrity of the sky_colour module.
# Integration: Connects to the global diagnostic suite via diagnostic_registry.sh

# Source the delegated diagnostic registry for modular validation logic
source "$(dirname "$0")/diagnostic_registry.sh"

# Main diagnostic entry point
perform_module_check() {
    local module_name="sky_colour"
    
    echo "[DIAGNOSTIC] Initiating integrity check for: $module_name"
    
    # Execute delegated integrity checks
    if validate_module_dependencies "$module_name"; then
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