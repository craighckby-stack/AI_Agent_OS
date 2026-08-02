#!/bin/bash
# calculator/run.sh — Deterministic math evaluation module.
#
# Role: Orchestrates safe mathematical evaluation with pre-flight diagnostic checks.
# Integration: Connects to eval.py for computation and diagnostic_hook.sh for system integrity.
#
# This script serves as the entry point for the Calculator module, ensuring
# that all environment dependencies are verified before processing requests.
#
# DIAGNOSTIC INTEGRITY: This module is gated by the Tessera Enterprise kernel diagnostic engine.

set -e

# --- Initialization ---
MODULE_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$MODULE_DIR/diagnostic_telemetry.sh"

# --- Pre-flight Diagnostic Check ---
# Validate environment integrity before execution
if [ -f "$MODULE_DIR/diagnostic_hook.sh" ]; then
    source "$MODULE_DIR/diagnostic_hook.sh"
    if ! run_module_diagnostics; then
        log_error "Diagnostic pre-flight check failed. Integrity breach detected."
        exit 1
    fi
fi

# Verify Python environment
if ! verify_python_env; then
    exit 1
fi

REQUEST="${AI_AGENT_REQUEST:-}"
if [ -z "$REQUEST" ]; then
    log_error "AI_AGENT_REQUEST not set"
    exit 1
fi

CACHE_DIR="$MODULE_DIR/.cache"
mkdir -p "$CACHE_DIR"

# Per-expression cache key
REQ_NORM=$(echo -n "$REQUEST" | tr '[:upper:]' '[:lower:]' | tr -s ' ')
CACHE_KEY=$(echo -n "$REQ_NORM" | md5sum | cut -d' ' -f1)
CACHE_FILE="$CACHE_DIR/${CACHE_KEY}.txt"

# Cache hit?
if [ -f "$CACHE_FILE" ]; then
    log_info "Cache hit for request: $REQUEST"
    cat "$CACHE_FILE"
    cleanup_transient_state
    exit 0
fi

# Cache miss — evaluate
log_info "Cache miss — evaluating: $REQUEST"
RESULT=$(python3 "$MODULE_DIR/eval.py" "$REQUEST" 2>&1) || {
    log_error "Evaluation failed: $RESULT"
    cleanup_transient_state
    exit 1
}

# Cache and output
echo -n "$RESULT" > "$CACHE_FILE"
log_info "Result generated for: $REQUEST"
echo "$RESULT"

# --- Teardown ---
# Ensure no transient state leaks into the kernel environment
cleanup_transient_state