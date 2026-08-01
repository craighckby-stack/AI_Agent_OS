"""
DIAGNOSTIC CONTEXT
Role: Maintains the global state of system health for the kernel lifecycle.
"""

class DiagnosticContext:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DiagnosticContext, cls).__new__(cls)
            cls._instance.status = "INITIALIZING"
            cls._instance.history = []
        return cls._instance

    def update_status(self, new_status: str):
        self.status = new_status
        self.history.append(new_status)

    def get_current_health(self) -> str:
        return self.status