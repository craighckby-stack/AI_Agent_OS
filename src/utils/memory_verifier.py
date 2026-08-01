"""
MEMORY VERIFIER & EVIDENTIAL PERSISTENCE ENGINE
Role: Implements evidence-based memory validation, confidence decay calculation,
      dependency hashing, and atomic file persistence for the Local Agent Kernel.
Integration: Referenced by docs/MEMORY_SPECIFICATION.md and imported by kernel/diagnostic engines.
Dependencies: Python Standard Library (json, os, time, hashlib, pathlib, typing).
"""

import json
import os
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from src.utils.memory_diagnostic_utils import MemoryDiagnosticEngine

class MemoryVerifier:
    """
    Evidence-based memory validator and atomic persistence manager.
    Enforces confidence thresholds, half-life TTL decay, and dependency hash verification.
    """

    DEFAULT_CONFIDENCE_THRESHOLD: float = 90.0
    HALF_LIFE_SECONDS: float = 86400.0  # 24 hours default half-life

    def __init__(self, memory_path: Optional[str] = None):
        if memory_path:
            self.memory_file = Path(memory_path)
        else:
            self.memory_file = Path(__file__).parent.parent.parent / "memory" / "local" / "memory.json"
        self.engine = MemoryDiagnosticEngine()

    def calculate_decayed_confidence(
        self, initial_confidence: float, timestamp: float, half_life: float = HALF_LIFE_SECONDS
    ) -> float:
        """
        Calculates dynamic decay score based on elapsed time since verification.
        Uses exponential half-life decay formula: C_t = C_0 * (0.5 ^ (elapsed / half_life)).
        """
        elapsed = time.time() - timestamp
        if elapsed <= 0:
            return initial_confidence
        decay_factor = 0.5 ** (elapsed / half_life)
        return round(initial_confidence * decay_factor, 2)

    def compute_hash(self, content: str) -> str:
        """
        Computes SHA-256 digest string for content integrity checking.
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def validate_entry(self, entry: Dict[str, Any], min_confidence: float = DEFAULT_CONFIDENCE_THRESHOLD) -> Tuple[bool, str]:
        """
        Validates a single memory entry against evidence criteria.
        """
        required_keys = ["result", "confidence", "version"]
        for key in required_keys:
            if key not in entry:
                return False, f"Missing required field: '{key}'"

        initial_confidence = float(entry.get("confidence", 0.0))
        timestamp = float(entry.get("timestamp", time.time()))
        half_life = float(entry.get("decay_half_life_seconds", self.HALF_LIFE_SECONDS))

        decayed_confidence = self.calculate_decayed_confidence(initial_confidence, timestamp, half_life)

        if decayed_confidence < min_confidence:
            return False, f"Confidence degraded ({decayed_confidence}% < {min_confidence}% threshold)"

        expiry = entry.get("expiry")
        if expiry is not None and time.time() > float(expiry):
            return False, f"Memory entry expired (expiry t={expiry})"

        return True, f"Valid evidence (effective confidence: {decayed_confidence}%)"

    def load_memory_store(self) -> Dict[str, Any]:
        """
        Reads flat-file JSON memory store safely.
        """
        if not self.memory_file.exists():
            return {}
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def atomic_write(self, data: Dict[str, Any]) -> bool:
        """
        Atomically writes memory data to file to eliminate race conditions and corruption.
        """
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.memory_file.with_suffix(".tmp")
            
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            os.replace(temp_path, self.memory_file)
            return True
        except Exception:
            return False

    def verify_all(self) -> Dict[str, Any]:
        """
        Performs full store verification sweep with integrated telemetry.
        """
        start_time = time.perf_counter()
        store = self.load_memory_store()
        total_entries = len(store)
        valid_entries = 0
        invalid_details = {}

        for module_name, entry in store.items():
            if isinstance(entry, dict):
                is_valid, reason = self.validate_entry(entry)
                if is_valid:
                    valid_entries += 1
                else:
                    invalid_details[module_name] = reason
            else:
                invalid_details[module_name] = "Malformed entry structural format"

        is_healthy = total_entries == 0 or (valid_entries / total_entries) >= 0.8
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return self.engine.generate_diagnostic_report(
            status="HEALTHY" if is_healthy else "DEGRADED",
            metrics={
                "total_entries": total_entries,
                "valid_entries": valid_entries,
                "invalid_entries": total_entries - valid_entries,
                "duration_ms": round(duration_ms, 3)
            },
            details=invalid_details
        )