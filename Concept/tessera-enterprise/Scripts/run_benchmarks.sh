#!/bin/bash
# scripts/run_benchmarks.sh
# Role: Orchestrates benchmark execution with pre-flight diagnostic validation and telemetry.
# Integration: Connects to the Enterprise Diagnostic Engine via diagnostic_hook.sh.
# Architecture: Diagnostic Integrity / Zero-Leak Standard

set -euo pipefail

LOG_FILE="logs/benchmark_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs

# --- ZERO-LEAK CLEANUP TRAP ---
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "[ERROR] Benchmark suite failed at $(date). Check $LOG_FILE for details." | tee -a "$LOG_FILE"
    fi
    exit $exit_code
}
trap cleanup EXIT

# --- PRE-FLIGHT DIAGNOSTIC VALIDATION ---
if [ -f "./scripts/diagnostic_hook.sh" ]; then
    echo "[$(date +%T)] [DIAGNOSTIC] Running pre-flight environment validation..." | tee -a "$LOG_FILE"
    if ! bash ./scripts/diagnostic_hook.sh --silent >> "$LOG_FILE" 2>&1; then
        echo "[ERROR] Diagnostic check failed. Aborting benchmarks to prevent corrupted results." | tee -a "$LOG_FILE"
        exit 1
    fi
fi

echo "[$(date +%T)] Running Tessera benchmark suite..." | tee -a "$LOG_FILE"
echo "================================" | tee -a "$LOG_FILE"

# [1/2] Cost model benchmark
echo "[$(date +%T)] [1/2] Executing cost model benchmark..." | tee -a "$LOG_FILE"
python3 -m benchmarks.cost_model >> "$LOG_FILE" 2>&1

# [2/2] Semantic radius benchmark
echo "[$(date +%T)] [2/2] Executing semantic radius benchmark..." | tee -a "$LOG_FILE"
python3 -m benchmarks.semantic_radius >> "$LOG_FILE" 2>&1

echo "[$(date +%T)] ✅ Benchmarks complete. Results logged to $LOG_FILE" | tee -a "$LOG_FILE"