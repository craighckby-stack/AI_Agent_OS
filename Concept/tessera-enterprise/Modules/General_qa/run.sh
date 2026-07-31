#!/bin/bash
# general_qa/run.sh — LLM-backed fallback module with per-query disk cache.
#
# Invoked by the kernel with AI_AGENT_REQUEST env var set to the user query.
# Uses the z-ai CLI (z-ai-web-dev-sdk) for LLM calls. To use a different
# LLM, replace the z-ai call below with your preferred SDK.
#
# CACHING:
#   Output is cached per-query by md5(normalized request). Repeat queries
#   for the same phrasing return instantly with no LLM call. The kernel's
#   intent-clustered cache handles cross-phrasing deduplication at a higher
#   level (this module uses cluster_key: request, so each phrasing gets
#   its own slot here).

set -e

REQUEST="${AI_AGENT_REQUEST:-}"
if [ -z "$REQUEST" ]; then
    echo "[general_qa error] AI_AGENT_REQUEST not set"
    exit 1
fi

MODULE_DIR="$(cd "$(dirname "$0")" && pwd)"
CACHE_DIR="$MODULE_DIR/.cache"
mkdir -p "$CACHE_DIR"

# Per-query cache key
REQ_NORM=$(echo -n "$REQUEST" | tr '[:upper:]' '[:lower:]' | tr -s ' ')
CACHE_KEY=$(echo -n "$REQ_NORM" | md5sum | cut -d' ' -f1)
CACHE_FILE="$CACHE_DIR/${CACHE_KEY}.json"

# Cache hit?
if [ -f "$CACHE_FILE" ]; then
    ANSWER=$(python3 -c "
import json
try:
    d = json.load(open('$CACHE_FILE'))
    print(d.get('answer', ''))
except Exception:
    print('')
")
    if [ -n "$ANSWER" ]; then
        echo "[general_qa cache hit] $REQUEST"
        echo "$ANSWER"
        exit 0
    fi
fi

# Cache miss — call the LLM
echo "[general_qa cache miss — calling LLM] $REQUEST" >&2
TMP_OUT=$(mktemp /tmp/general_qa_XXXXXX.json)
trap "rm -f $TMP_OUT" EXIT

SYS_PROMPT="You are a concise factual assistant. Answer in 1-3 sentences. No headers, no markdown, no extra commentary."

# Use z-ai CLI if available, else fall back to curl + OpenAI-compatible API
if command -v z-ai >/dev/null 2>&1; then
    z-ai chat --system "$SYS_PROMPT" -p "$REQUEST" -o "$TMP_OUT" 2>/dev/null
else
    # Fallback: direct curl to OpenAI-compatible endpoint
    API_KEY="${OPENAI_API_KEY:-}"
    API_URL="${OPENAI_API_URL:-https://api.openai.com/v1/chat/completions}"
    if [ -z "$API_KEY" ]; then
        echo "[general_qa error] No LLM available (z-ai not found, OPENAI_API_KEY not set)" >&2
        exit 1
    fi
    curl -s -X POST "$API_URL" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"$SYS_PROMPT\"},{\"role\":\"user\",\"content\":\"$REQUEST\"}]}" \
        > "$TMP_OUT"
fi

# Extract answer + token usage
python3 -c "
import json
d = json.load(open('$TMP_OUT'))
answer = d['choices'][0]['message']['content'].strip()
usage = d.get('usage', {})
out = {
    'answer': answer,
    'prompt_tokens': usage.get('prompt_tokens', 0),
    'completion_tokens': usage.get('completion_tokens', 0),
    'total_tokens': usage.get('total_tokens', 0),
    'model': d.get('model', 'unknown'),
}
json.dump(out, open('$CACHE_FILE', 'w'), indent=2)
print(answer)
"
