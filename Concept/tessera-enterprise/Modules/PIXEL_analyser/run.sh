#!/bin/bash
# pixel_analyzer/run.sh — Deep image color analysis module.
#
# INVOCATION:
#   kernel.py sets AI_AGENT_REQUEST to the user's natural-language request.
#   This module extracts an image path from the request, OR falls back to
#   a default test image if none is provided.
#
# OUTPUT:
#   Structured JSON report with RGB means, dominant colors (k-means),
#   brightness histogram, hue distribution, and atmospheric interpretation.
#
# CACHING:
#   Output is cached per-image by file hash. Repeated analysis of the same
#   image returns instantly with zero compute cost. The kernel's
#   intent-clustered cache (extract:image) ALSO means all phrasings about
#   the same image share one slot at the kernel level.

set -e

REQUEST="${AI_AGENT_REQUEST:-}"
MODULE_DIR="$(cd "$(dirname "$0")" && pwd)"
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
    echo "[pixel_analyzer cache hit] image=$IMAGE_PATH hash=$IMAGE_HASH"
    cat "$CACHE_FILE"
    exit 0
fi

# Cache miss — run the analysis
echo "[pixel_analyzer cache miss — running analysis] image=$IMAGE_PATH" >&2
python3 "$MODULE_DIR/analyze.py" "$IMAGE_PATH" > "$CACHE_FILE"
cat "$CACHE_FILE"
