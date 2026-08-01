#!/bin/bash
# scripts/release.sh — Cut a new Tessera release.
# Role: Orchestrates version bumping, changelog updates, and git tagging.
# Integration: Connects to the Enterprise Diagnostic Engine for pre-flight validation.
# Usage: ./scripts/release.sh 0.2.0

set -e

# --- Diagnostic & Integrity Configuration ---
LOG_FILE="logs/release_lifecycle.log"
mkdir -p logs

log_event() {
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] $1" | tee -a "$LOG_FILE"
}

# --- Zero-Leak Cleanup Trap ---
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_event "[ERROR] Release process failed with code $exit_code. Cleaning up artifacts..."
        rm -f pyproject.toml.bak
    fi
}
trap cleanup EXIT

# --- Pre-flight Diagnostic Hook ---
if [ -f "scripts/diagnostic_hook.sh" ]; then
    log_event "[DIAGNOSTIC] Running pre-flight integrity checks..."
    if ! bash scripts/diagnostic_hook.sh --release-mode; then
        log_event "[ERROR] Diagnostic check failed. Aborting release."
        exit 1
    fi
fi

VERSION="${1:?Usage: ./scripts/release.sh <version>}"
log_event "Initiating Tessera release v$VERSION..."

# Update version in pyproject.toml
sed -i.bak "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml
rm pyproject.toml.bak

# Update CHANGELOG.md
python3 -c "
import re
from datetime import date
with open('CHANGELOG.md') as f:
    content = f.read()
today = date.today().isoformat()
new_section = f'## [{VERSION}] - {today}'
content = content.replace('## [Unreleased]', f'## [Unreleased]\n\n{new_section}', 1)
with open('CHANGELOG.md', 'w') as f:
    f.write(content)
"

# Commit and tag
git add pyproject.toml CHANGELOG.md
git commit -m "release: v$VERSION"
git tag "v$VERSION"

# Post-release verification
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    log_event "[SUCCESS] Release v$VERSION tagged successfully."
else
    log_event "[ERROR] Tagging failed."
    exit 1
fi

echo ""
echo "✅ Release v$VERSION prepared."
echo "   To publish: git push origin main --tags"
echo "   (The release.yml GitHub Action will publish to PyPI automatically.)"