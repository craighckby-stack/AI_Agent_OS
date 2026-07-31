#!/bin/bash
# calculator/run.sh — Deterministic math evaluation module.
#
# Extracts a mathematical expression from the request and evaluates it
# safely using Python's ast module. No LLM, no approximation — exact
# arithmetic, every time.

set -e

REQUEST="${AI_AGENT_REQUEST:-}"
if [ -z "$REQUEST" ]; then
    echo "[calculator error] AI_AGENT_REQUEST not set"
    exit 1
fi

MODULE_DIR="$(cd "$(dirname "$0")" && pwd)"
CACHE_DIR="$MODULE_DIR/.cache"
mkdir -p "$CACHE_DIR"

# Per-expression cache key
REQ_NORM=$(echo -n "$REQUEST" | tr '[:upper:]' '[:lower:]' | tr -s ' ')
CACHE_KEY=$(echo -n "$REQ_NORM" | md5sum | cut -d' ' -f1)
CACHE_FILE="$CACHE_DIR/${CACHE_KEY}.txt"

# Cache hit?
if [ -f "$CACHE_FILE" ]; then
    echo "[calculator cache hit] $REQUEST"
    cat "$CACHE_FILE"
    exit 0
fi

# Cache miss — evaluate
echo "[calculator cache miss — evaluating] $REQUEST" >&2
RESULT=$(python3 "$MODULE_DIR/eval.py" "$REQUEST" 2>&1) || {
    echo "[calculator error] $RESULT" >&2
    exit 1
}

# Cache and output
echo -n "$RESULT" > "$CACHE_FILE"
echo "[calculator result] $REQUEST"
echo "$RESULT"
