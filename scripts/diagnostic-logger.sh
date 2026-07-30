#!/usr/bin/env bash
# Shared diagnostic logging utilities

log_info() { echo "[INFO] $(date -u +'%Y-%m-%dT%H:%M:%SZ') - $1"; }
log_warn() { echo "[WARN] $(date -u +'%Y-%m-%dT%H:%M:%SZ') - $1"; }
log_error() { echo "[ERROR] $(date -u +'%Y-%m-%dT%H:%M:%SZ') - $1"; }