#!/bin/bash
# scripts/run_benchmarks.sh — Run the full benchmark suite.
# Role: Orchestrates benchmark execution with pre-flight diagnostic validation.
# Integration: Connects to the Enterprise Diagnostic Engine via diagnostic_hook.sh.

set -e

# --- PRE-FLIGHT DIAGNOSTIC VALIDATION ---
# Ensure the environment is healthy before running benchmarks.
if [ -f "./scripts/diagnostic_hook.sh" ]; then
    echo "[DIAGNOSTIC] Running pre-flight environment validation..."
    bash ./scripts/diagnostic_hook.sh --silent
    if [ $? -ne 0 ]; then
        echo "[ERROR] Diagnostic check failed. Aborting benchmarks to prevent corrupted results."
        exit 1
    fi
fi

echo "Running Tessera benchmark suite..."
echo "================================"

echo ""
echo "[1/2] Cost model benchmark..."
python3 -m benchmarks.cost_model

echo ""
echo "[2/2] Semantic radius benchmark..."
python3 -m benchmarks.semantic_radius

echo ""
echo "✅ Benchmarks complete."