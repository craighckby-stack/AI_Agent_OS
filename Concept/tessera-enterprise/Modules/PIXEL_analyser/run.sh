#!/bin/bash
# pixel_analyzer/run.sh — Deep image color analysis module.
#
# ARCHITECTURAL ROLE:
#   Executes image color analysis with pre-flight diagnostic validation.
#   Integrates with the Enterprise Diagnostic Engine to ensure environment stability.
#
# INVOCATION:
#   kernel.py sets AI_AGENT_REQUEST to the user's natural-language request.
#
# OUTPUT:
#   Structured JSON report with RGB means, dominant colors, and atmospheric interpretation.

set -e

# Cleanup trap for Zero-Leak compliance
cleanup() {
    exit_code=$?
    [ $exit_code -ne 0 ] && echo "[pixel_analyzer] Execution failed with code $exit_code" >&2
    trap - EXIT
}
trap cleanup EXIT

MODULE_DIR="$(cd "$(dirname "$0")" && pwd)"

# 1. PRE-FLIGHT DIAGNOSTIC HOOK
# Ensures environment integrity before compute-heavy analysis
if [ -f "$MODULE_DIR/diagnostic_hook.sh" ]; then
    source "$MODULE_DIR/diagnostic_hook.sh"
    if ! run_preflight_diagnostics; then
        echo "[pixel_analyzer] Diagnostic check failed. Aborting execution." >&2
        exit 1
    fi
fi

REQUEST="${AI_AGENT_REQUEST:-}"
CACHE_DIR="$MODULE_DIR/.cache"
mkdir -p "$CACHE_DIR"

# Resolve image path: try to extract from request, else use default
DEFAULT_IMAGE="$MODULE_DIR/../../benchmarks/fixtures/sample.jpg"

# Look for a file path in the request
IMAGE_PATH=""
if [[ "$REQUEST" =~ ([^ ]+\.(jpg|jpeg|png|webp|bmp|gif)) ]]; then
    IMAGE_PATH="${BASH_REMATCH[1]}"
    # Resolve relative to repo root if not absolute
    if [[ ! -f "$IMAGE_PATH" ]]; then
        IMAGE_PATH="$MODULE_DIR/../../$IMAGE_PATH"
    fi
fi
if [ -z "$IMAGE_PATH" ] || [ ! -f "$IMAGE_PATH" ]; then
    IMAGE_PATH="$DEFAULT_IMAGE"
fi

if [ ! -f "$IMAGE_PATH" ]; then
    echo "[pixel_analyzer error] No image found at $IMAGE_PATH"
    exit 1
fi

# Compute cache key: hash of image file content
IMAGE_HASH=$(md5sum "$IMAGE_PATH" | cut -d' ' -f1)
CACHE_FILE="$CACHE_DIR/${IMAGE_HASH}.json"

# Cache hit?
if [ -f "$CACHE_FILE" ]; then
    echo "[pixel_analyzer telemetry] status=CACHE_HIT image=$IMAGE_PATH hash=$IMAGE_HASH" >&2
    cat "$CACHE_FILE"
    exit 0
fi

# Cache miss — run the analysis
echo "[pixel_analyzer telemetry] status=CACHE_MISS image=$IMAGE_PATH" >&2
python3 "$MODULE_DIR/analyze.py" "$IMAGE_PATH" > "$CACHE_FILE"
cat "$CACHE_FILE"