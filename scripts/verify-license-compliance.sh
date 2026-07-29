#!/usr/bin/env bash
# ==============================================================================
# LICENSE COMPLIANCE VERIFICATION CONTROLLER
# ==============================================================================
# Purpose: Scans the repository to ensure all source files contain the required
#          copyright notice as mandated by the PolyForm Noncommercial License.
# Usage: bash scripts/verify-license-compliance.sh
# ==============================================================================

set -euo pipefail

REQUIRED_NOTICE="Required Notice: Copyright craighckby-stack"
ALT_NOTICE="Copyright craighckby-stack"

# Directories and file extensions to scan
SCAN_EXTENSIONS=("py" "sh" "ts" "tsx" "js" "jsx" "go" "cpp" "h" "cs")
EXCLUDE_DIRS=("node_modules" "dist" "build" ".git" "memory" "venv" "__pycache__")

echo "🔍 Starting license compliance scan..."

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
            # Check if file contains either the required notice or the alternative notice
            if ! grep -qF "$REQUIRED_NOTICE" "$file" && ! grep -qF "$ALT_NOTICE" "$file"; then
                NON_COMPLIANT_FILES+=("$file")
            fi
        fi
    done < <(find . -type f -name "*.$ext" "${EXCLUDE_ARGS[@]}")
done

echo "📊 Scan complete. Scanned $TOTAL_SCANNED files."

if [ ${#NON_COMPLIANT_FILES[@]} -eq 0 ]; then
    echo "✅ Success: All scanned files comply with the license notice requirements!"
    exit 0
else
    echo "❌ Error: Found ${#NON_COMPLIANT_FILES[@]} non-compliant file(s) missing the copyright notice:"
    for file in "${NON_COMPLIANT_FILES[@]}"; do
        echo "   - $file"
    done
    echo "💡 Please add the following comment to the top of these files:"
    echo "   # Required Notice: Copyright craighckby-stack"
    exit 1
fi