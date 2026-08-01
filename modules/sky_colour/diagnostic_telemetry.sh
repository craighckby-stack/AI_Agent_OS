#!/bin/bash
# DIAGNOSTIC TELEMETRY UTILITY
# Role: Generates structured diagnostic telemetry for module integrity checks.

format_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

generate_diagnostic_report() {
    local module=$1
    local status=$2
    local start=$3
    local end=$4
    local duration=$(( (end - start) / 1000000 ))

    local report=$(cat <<EOF
{
  "module": "$module",
  "status": "$status",
  "timestamp": "$(format_timestamp)",
  "duration_ms": $duration,
  "version": "1.1.0-DIAGNOSTIC-AWARE"
}
EOF
    )
    
    echo "[TELEMETRY] $report" >&2
}