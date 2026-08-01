"""
SCHEMA TELEMETRY UTILITY
Role: Measures and records the performance and health of validation cycles.
Siphoned from: AI_Agent_OS diagnostic_engine_utils.py
"""

import time
from typing import Dict, Any
from contextlib import contextmanager

class SchemaTelemetry:
    def __init__(self):
        self.start_time = 0
        self.duration_ms = 0
        self.results = {}

    @classmethod
    @contextmanager
    def track_validation_cycle(cls):
        telemetry = cls()
        telemetry.start_time = time.perf_counter()
        try:
            yield telemetry
        finally:
            telemetry.duration_ms = (time.perf_counter() - telemetry.start_time) * 1000.0
            # In a real system, this would push to a global diagnostic context
            # print(f"[TELEMETRY] Validation cycle completed in {telemetry.duration_ms:.3f}ms")

    def record_results(self, results: Dict[str, Any]):
        self.results = results