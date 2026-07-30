"""
DIAGNOSTIC CONTEXT MANAGER
Role: Maintains the state of system health across execution cycles.
"""

class DiagnosticContext:
    def __init__(self):
        self.last_status = "UNKNOWN"
        self.last_check = None

    def update_status(self, status: str):
        self.last_status = status
        self.last_check = __import__('datetime').datetime.utcnow().isoformat()

    def get_context(self):
        return {"status": self.last_status, "last_check": self.last_check}