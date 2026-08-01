import datetime
import time
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
    """Retrieves current system performance metrics."""
    return {
        "uptime_seconds": time.perf_counter(),
        "status": "OPERATIONAL"
    }