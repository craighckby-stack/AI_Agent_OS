"""
KERNEL CONTEXT UTILITIES
Role: Provides core diagnostic telemetry, timestamping, and system metric retrieval.
Integration: Used by kernel_context.py and diagnostic_engine.py to ensure consistent telemetry across the system.
Dependencies: datetime, time, typing
"""

from __future__ import annotations
import datetime
import time
import os
from typing import Dict, Any

def format_timestamp() -> str:
    """Returns ISO 8601 formatted UTC timestamp with Z suffix."""
    return datetime.datetime.utcnow().isoformat() + 'Z'

def generate_telemetry_metadata() -> Dict[str, Any]:
    """Generates standard telemetry metadata for diagnostic results."""
    return {
        "timestamp": time.time(),
        "thread_id": id(time.time()),
        "version": "1.0.0-DIAGNOSTIC-AWARE"
    }

def get_system_metrics() -> Dict[str, Any]:
    """Retrieves current system performance metrics and operational status."""
    return {
        "uptime_seconds": round(time.perf_counter(), 3),
        "status": "OPERATIONAL",
        "process_id": os.getpid(),
        "telemetry": generate_telemetry_metadata()
    }