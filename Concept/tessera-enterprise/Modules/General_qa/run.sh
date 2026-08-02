#!/bin/bash
# general_qa/run.sh — LLM-backed fallback module with per-query disk cache.
# Role: Enterprise-grade QA module with pre-flight diagnostic validation.
# Integration: Connects to diagnostic_hook.sh and telemetry_helper.sh.
# Version: 1.1.0-DIAGNOSTIC-AWARE

set -e

# 1. INITIALIZATION & TELEMETRY
MODULE_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$MODULE_DIR/telemetry_helper.sh"

# 2. PRE-FLIGHT DIAGNOSTIC CHECK
if [ -f "$MODULE_DIR/diagnostic_hook.sh" ]; then
    source "$MODULE_DIR/diagnostic_hook.sh"
    if ! perform_pre_flight_check; then
        log_event "error" "Pre-flight diagnostic check failed."
        exit 1
    fi
fi

# 3. CORE EXECUTION
REQUEST="${AI_AGENT_REQUEST:-}"
if [ -z "$REQUEST" ]; then
    log_event "error" "AI_AGENT_REQUEST not set"
    exit 1
fi

CACHE_DIR="$MODULE_DIR/.cache"
mkdir -p "$CACHE_DIR"

# Per-query cache key generation
REQ_NORM=$(echo -n "$REQUEST" | tr '[:upper:]' '[:lower:]' | tr -s ' ')
CACHE_KEY=$(echo -n "$REQ_NORM" | md5sum | cut -d' ' -f1)
CACHE_FILE="$CACHE_DIR/${CACHE_KEY}.json"

# Cache hit validation
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
        log_event "info" "Cache hit for request: ${CACHE_KEY}"
        echo "$ANSWER"
        exit 0
    fi
fi

# 4. LLM ORCHESTRATION (Cache miss)
log_event "info" "Cache miss — calling LLM"
TMP_OUT=$(mktemp /tmp/general_qa_XXXXXX.json)
trap "cleanup_transient '$TMP_OUT'" EXIT

SYS_PROMPT="You are a concise factual assistant. Answer in 1-3 sentences. No headers, no markdown, no extra commentary."

if command -v z-ai >/dev/null 2>&1; then
    z-ai chat --system "$SYS_PROMPT" -p "$REQUEST" -o "$TMP_OUT" 2>/dev/null
else
    API_KEY="${OPENAI_API_KEY:-}"
    API_URL="${OPENAI_API_URL:-https://api.openai.com/v1/chat/completions}"
    curl -s -X POST "$API_URL" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"gpt-4o-mini\",\"messages\":[{\"role\":\"system\",\"content\":\"$SYS_PROMPT\"},{\"role\":\"user\",\"content\":\"$REQUEST\"}]}" \
        > "$TMP_OUT"
fi

# 5. POST-PROCESSING & PERSISTENCE
python3 -c "
import json
try:
    with open('$TMP_OUT', 'r') as f:
        d = json.load(f)
    answer = d['choices'][0]['message']['content'].strip()
    usage = d.get('usage', {})
    out = {
        'answer': answer,
        'prompt_tokens': usage.get('prompt_tokens', 0),
        'completion_tokens': usage.get('completion_tokens', 0),
        'total_tokens': usage.get('total_tokens', 0),
        'model': d.get('model', 'unknown'),
    }
    with open('$CACHE_FILE', 'w') as f:
        json.dump(out, f, indent=2)
    print(answer)
except Exception as e:
    print(f'Error processing response: {e}')
    exit(1)
"