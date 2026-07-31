#!/bin/bash
# scripts/dev_install.sh — Set up Tessera for development.
set -e

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
