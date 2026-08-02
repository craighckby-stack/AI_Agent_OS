#!/bin/bash
# ==============================================================================
# DIAGNOSTIC HOOK: CALCULATOR MODULE
# Role: Validates kernel integrity, environment dependencies, and file system 
#       permissions for the Calculator module within the Tessera Enterprise.
# Integration: Called by the module loader before any execution of eval.py.
# ==============================================================================

# Import diagnostic utilities
source "$(dirname "$0")/diagnostic_utils.sh"

MODULE_DIR="$(dirname "$0")"

run_module_diagnostics() {
    log_info "Initiating pre-flight integrity check for Calculator Module..."

    # 1. Verify Python environment availability
    if ! verify_dependency "python3"; then
        return 1
    fi
    
    # 2. Verify core module component existence
    if [ ! -f "$MODULE_DIR/eval.py" ]; then
        log_error "Critical component missing: eval.py"
        return 1
    fi
    
    # 3. Verify directory write permissions for cache/state persistence
    if ! check_write_access "$MODULE_DIR"; then
        return 1
    fi

    # 4. Verify Python environment can execute the module
    if ! python3 -c "import sys; print(sys.version)" &> /dev/null; then
        log_error "Python environment is unstable or corrupted."
        return 1
    fi
    
    log_info "Integrity check passed. Environment is ready."
    return 0
}

# Execute diagnostics if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_module_diagnostics
    exit $?
fi