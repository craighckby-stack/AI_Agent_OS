#!/bin/bash
# scripts/run_benchmarks.sh — Run the full benchmark suite.
set -e

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
