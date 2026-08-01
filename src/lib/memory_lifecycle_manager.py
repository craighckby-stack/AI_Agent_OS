"""
MEMORY LIFECYCLE MANAGER
Role: State machine for memory entry transitions (EVIDENTIAL -> STALE -> PURGED).
Integrates with: memory_decay_engine.py and diagnostic_engine.py
"""

from enum import Enum
from typing import Dict, Any, Optional
from src.utils.memory_decay_engine import calculate_decay

class MemoryState(Enum):
    EVIDENTIAL = "EVIDENTIAL"
    STALE = "STALE"
    INVALIDATED = "INVALIDATED"
    PURGED = "PURGED"
    UNKNOWN = "UNKNOWN"

class MemoryLifecycleManager:
    def __init__(self, threshold: float = 0.90):
        self.threshold = threshold

    def determine_state(self, entry: Dict[str, Any], current_hash: Optional[str] = None) -> MemoryState:
        """Determines the current state of a memory entry based on decay and integrity."""
        # 1. Check Cryptographic Integrity
        stored_hash = entry.get('dependency_hash')
        if current_hash and stored_hash and current_hash != stored_hash:
            return MemoryState.INVALIDATED

        # 2. Check Expiry
        import time
        if entry.get('expiry') and time.time() > entry['expiry']:
            return MemoryState.PURGED

        # 3. Check Decay
        decay_res = calculate_decay(
            entry.get('confidence', 0.0),
            entry.get('timestamp', 0.0),
            entry.get('decay_half_life_seconds', 86400.0),
            self.threshold
        )

        if not decay_res.is_valid:
            return MemoryState.STALE

        return MemoryState.EVIDENTIAL

    def get_transition_action(self, state: MemoryState) -> str:
        """Returns the recommended action for a given state."""
        actions = {
            MemoryState.EVIDENTIAL: "TRUST_AND_USE",
            MemoryState.STALE: "BACKGROUND_REFRESH",
            MemoryState.INVALIDATED: "IMMEDIATE_PURGE",
            MemoryState.PURGED: "RE_EXECUTE_MODULE",
            MemoryState.UNKNOWN: "DIAGNOSTIC_AUDIT"
        }
        return actions.get(state, "NO_ACTION")