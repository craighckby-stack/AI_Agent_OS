#!/usr/bin/env bash
# Diagnostic Utility for License Compliance

log_diagnostic() {
    echo "[DIAGNOSTIC] $(date -u +'%Y-%m-%dT%H:%M:%SZ') - $1"
}

report_success() {
    echo "✅ Success: $1"
}

report_failure() {
    echo "❌ Error: $1"
    echo "💡 Please add: # Required Notice: Copyright craighckby-stack"
}