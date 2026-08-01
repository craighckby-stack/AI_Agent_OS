#!/bin/bash
# scripts/release.sh — Cut a new Tessera release.
# Role: Orchestrates version bumping, changelog updates, and git tagging.
# Integration: Connects to the Enterprise Diagnostic Engine for pre-flight validation.
# Usage: ./scripts/release.sh 0.2.0

set -e

# --- Pre-flight Diagnostic Hook ---
# Ensures environment integrity before mutation
if [ -f "scripts/diagnostic_hook.sh" ]; then
    echo "[DIAGNOSTIC] Running pre-flight integrity checks..."
    bash scripts/diagnostic_hook.sh --release-mode
    if [ $? -ne 0 ]; then
        echo "[ERROR] Diagnostic check failed. Aborting release."
        exit 1
    fi
fi

VERSION="${1:?Usage: ./scripts/release.sh <version>}"

echo "Cutting Tessera release v$VERSION..."

# Update version in pyproject.toml
sed -i.bak "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml
rm pyproject.toml.bak

# Update CHANGELOG.md — move [Unreleased] to [$VERSION]
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
print(f'Updated CHANGELOG.md with release date {today}')
"

# Commit and tag
git add pyproject.toml CHANGELOG.md
git commit -m "release: v$VERSION"
git tag "v$VERSION"

echo ""
echo "✅ Release v$VERSION prepared."
echo "   To publish: git push origin main --tags"
echo "   (The release.yml GitHub Action will publish to PyPI automatically.)"