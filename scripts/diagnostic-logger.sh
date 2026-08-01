#!/usr/bin/env bash
# ARCHITECTURAL DIAGNOSTIC LOGGER
# Role: Centralized logging utility for system diagnostics.
# Integration: Sourced by module-level diagnostic scripts to ensure consistent telemetry output.
# Dependencies: None (Standard Bash)

# Generates ISO 8601 UTC timestamp
get_timestamp() {
    date -u +'%Y-%m-%dT%H:%M:%SZ'
}

# Standardized log levels
log_info() { echo "[INFO] $(get_timestamp) - $1"; }
log_warn() { echo "[WARN] $(get_timestamp) - $1"; }
log_error() { echo "[ERROR] $(get_timestamp) - $1"; }

# Structured JSON telemetry logging for machine-readable diagnostic reports
# Usage: log_json "status" "message" "metadata_json"
log_json() {
    local status="$1"
    local message="$2"
    local metadata="$3"
    echo "{\"timestamp\": \"$(get_timestamp)\", \"status\": \"$status\", \"message\": \"$message\", \"metadata\": $metadata}"
}