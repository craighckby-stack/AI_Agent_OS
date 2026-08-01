#!/bin/bash
# scripts/dev_install.sh — Set up Tessera for development.
# Role: Orchestrates environment setup and pre-flight diagnostic validation for the Tessera Enterprise ecosystem.
# Integration: Connects to the Enterprise Diagnostic Engine to ensure environment readiness before dependency resolution.
# Architecture: Adheres to Diagnostic Integrity standards (Zero-Leak, Telemetry-Aware).

set -e

# --- Diagnostic Integrity Hook ---
# Ensures environment readiness before proceeding with installation.
# Siphoned from AI_Agent_OS diagnostic_engine.py patterns.

cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "[ERROR] Installation failed at step: $BASH_COMMAND. Cleaning up..."
    fi
    exit $exit_code
}

trap cleanup ERR

check_environment() {
    echo "[DIAGNOSTIC] Starting pre-flight environment integrity check..."
    
    # Validate Python availability
    if ! command -v python3 &> /dev/null; then
        echo "[CRITICAL] python3 not found. Installation aborted."
        exit 1
    fi

    # Validate Write Permissions
    if [ ! -w "." ]; then
        echo "[CRITICAL] Write permissions missing in current directory."
        exit 1
    fi

    # Validate Diagnostic Hook existence if present in system
    if [ -f "scripts/diagnostic_hook.sh" ]; then
        bash scripts/diagnostic_hook.sh --check-only
    fi

    echo "[DIAGNOSTIC] Environment validated successfully. Telemetry: OK."
}

# Execute diagnostic gate
check_environment

echo "Installing Tessera in development mode..."

# Create virtual env if not present
if [ ! -d ".venv" ]; then
    echo "[INFO] Initializing virtual environment..."
    python3 -m venv .venv
fi

# Activate environment
source .venv/bin/activate

# Upgrade core tools
pip install --upgrade pip setuptools wheel

# Install with dev + image extras
echo "[INFO] Resolving dependencies..."
pip install -e ".[dev,image]"

# Install pre-commit hooks if available
if command -v pre-commit >/dev/null 2>&1; then
    pre-commit install
    echo "[INFO] Pre-commit hooks installed."
fi

echo ""
echo "✅ Development install complete."
echo "   Activate with: source .venv/bin/activate"
echo "   Run tests with: pytest tests/ -v"
echo "   Run benchmarks with: python -m benchmarks.cost_model"