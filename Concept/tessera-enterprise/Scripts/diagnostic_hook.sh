#!/bin/bash
# Diagnostic Hook for Tessera Enterprise
# Validates environment state before critical operations.

check_git_status() {
    if [[ -n $(git status -s) ]]; then
        echo "[FAIL] Working directory is dirty. Commit changes first."
        return 1
    fi
    return 0
}

check_files_exist() {
    if [[ ! -f "pyproject.toml" ]] || [[ ! -f "CHANGELOG.md" ]]; then
        echo "[FAIL] Missing required release files."
        return 1
    fi
    return 0
}

echo "[DIAGNOSTIC] Validating system integrity..."
check_git_status && check_files_exist
exit $?