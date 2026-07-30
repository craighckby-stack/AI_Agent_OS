#!/usr/bin/env bash
# ==============================================================================
# LICENSE DIAGNOSTIC REGISTRY
# Role: Orchestrates complex validation logic for license compliance.
# Integration: Called by license-diagnostic-utils.sh.
# ==============================================================================

perform_license_integrity_check() {
    # Validate presence of mandatory license files
    local required_files=("LICENSE" "NOTICE")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "[ERROR] Missing mandatory file: $file" >&2
            return 1
        fi
    done
    return 0
}