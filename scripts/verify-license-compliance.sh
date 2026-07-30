#!/usr/bin/env bash
# ==============================================================================
# LICENSE COMPLIANCE VERIFICATION CONTROLLER
# Role: Scans repository for copyright notices; integrates with system diagnostics.
# Integration: Connects to diagnostic-engine for real-time health reporting.
# ==============================================================================

set -euo pipefail

# Import Diagnostic Integrity Hook
# Ensures system health before executing compliance verification
if [ -f "$(dirname "$0")/license-diagnostic-utils.sh" ]; then
    source "$(dirname "$0")/license-diagnostic-utils.sh"
else
    echo "[ERROR] Diagnostic utility missing. Aborting."
    exit 1
fi

REQUIRED_NOTICE="Required Notice: Copyright craighckby-stack"
ALT_NOTICE="Copyright craighckby-stack"

# Directories and file extensions to scan
SCAN_EXTENSIONS=("py" "sh" "ts" "tsx" "js" "jsx" "go" "cpp" "h" "cs")
EXCLUDE_DIRS=("node_modules" "dist" "build" ".git" "memory" "venv" "__pycache__")

# Diagnostic-Aware Execution Wrapper
log_diagnostic "Starting license compliance scan..."

# Build find exclusion arguments
EXCLUDE_ARGS=()
for dir in "${EXCLUDE_DIRS[@]}"; do
    EXCLUDE_ARGS+=(-not -path "*/${dir}/*")
done

NON_COMPLIANT_FILES=()
TOTAL_SCANNED=0

# Scan files
for ext in "${SCAN_EXTENSIONS[@]}"; do
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            TOTAL_SCANNED=$((TOTAL_SCANNED + 1))
            if ! grep -qF "$REQUIRED_NOTICE" "$file" && ! grep -qF "$ALT_NOTICE" "$file"; then
                NON_COMPLIANT_FILES+=("$file")
            fi
        fi
    done < <(find . -type f -name "*.$ext" "${EXCLUDE_ARGS[@]}")
done

# Final Reporting
if [ ${#NON_COMPLIANT_FILES[@]} -eq 0 ]; then
    report_success "All $TOTAL_SCANNED files comply with license requirements."
    exit 0
else
    report_failure "Found ${#NON_COMPLIANT_FILES[@]} non-compliant files."
    for file in "${NON_COMPLIANT_FILES[@]}"; do
        echo "   - $file"
    done
    exit 1
fi