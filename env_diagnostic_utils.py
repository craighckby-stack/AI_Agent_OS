import datetime

def log_diagnostic_event(component: str, status: str, message: str):
    """
    Logs diagnostic events for the environment loader.
    Siphoned from AI_Agent_OS diagnostic patterns.
    """
    timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
    print(f"[{timestamp}] [DIAGNOSTIC] [{component}] {status}: {message}")
