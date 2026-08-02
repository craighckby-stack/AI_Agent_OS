import sys
import json
import time

def report_diagnostic(status, message, details=None):
    """Standardized telemetry reporter for General_qa module."""
    payload = {
        "status": status,
        "message": message,
        "timestamp": time.time(),
        "details": details or {}
    }
    sys.stderr.write(json.dumps(payload) + "\n")

if __name__ == "__main__":
    # Simple CLI wrapper for diagnostic reporting
    status = sys.argv[1] if len(sys.argv) > 1 else "INFO"
    msg = sys.argv[2] if len(sys.argv) > 2 else "No message"
    report_diagnostic(status, msg)