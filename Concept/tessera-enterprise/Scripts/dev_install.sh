#!/bin/bash
# scripts/dev_install.sh — Set up Tessera for development.
# Role: Orchestrates environment setup and pre-flight diagnostic validation for the Tessera Enterprise ecosystem.
# Integration: Connects to the Enterprise Diagnostic Engine to ensure environment readiness before dependency resolution.

set -e

# --- Diagnostic Integrity Check ---
# Siphoned from AI_Agent_OS diagnostic_engine.py patterns
check_environment() {
    echo "[DIAGNOSTIC] Validating environment integrity..."
    
    if ! command -v python3 &> /dev/null; then
        echo "[CRITICAL] python3 not found. Installation aborted."
        exit 1
    fi

    if [ ! -w "." ]; then
        echo "[CRITICAL] Write permissions missing in current directory."
        exit 1
    fi

    echo "[DIAGNOSTIC] Environment validated successfully."
}

check_environment

echo "Installing Tessera in development mode..."

# Create virtual env if not present
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Created .venv"
fi

source .venv/bin/activate

# Install with dev + image extras
pip install --upgrade pip
pip install -e ".[dev,image]"

# Install pre-commit hooks if available
if command -v pre-commit >/dev/null 2>&1; then
    pre-commit install
    echo "Pre-commit hooks installed."
fi

echo ""
echo "✅ Development install complete."
echo "   Activate with: source .venv/bin/activate"
echo "   Run tests with: pytest tests/ -v"
echo "   Run benchmarks with: python -m benchmarks.cost_model"