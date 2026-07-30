from typing import Dict, Any, Optional
import datetime

class KernelContext:
    """Encapsulates execution metadata for the kernel lifecycle."""
    def __init__(self, request: str):
        self.request = request
        self.start_time = datetime.datetime.utcnow()
        self.metadata: Dict[str, Any] = {
            "session_id": id(self),
            "status": "INITIALIZED"
        }

    def update_status(self, status: str) -> None:
        self.metadata["status"] = status

    def get_report(self) -> Dict[str, Any]:
        return {
            "request": self.request,
            "duration": (datetime.datetime.utcnow() - self.start_time).total_seconds(),
            **self.metadata
        }