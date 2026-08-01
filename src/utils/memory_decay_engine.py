"""
MEMORY DECAY ENGINE
Role: Mathematical computation of evidential confidence decay.
Siphoned from: AI_Agent_OS Diagnostic Patterns
"""

from __future__ import annotations
import time
import math
from typing import Dict, Any, NamedTuple

class DecayResult(NamedTuple):
    current_confidence: float
    is_valid: bool
    delta_t: float

def calculate_decay(
    initial_confidence: float, 
    timestamp: float, 
    half_life: float = 86400.0,
    threshold: float = 0.90
) -> DecayResult:
    """
    Computes exponential decay of memory confidence.
    Formula: C(t) = C0 * 0.5^(delta_t / tau)
    """
    now = time.time()
    delta_t = max(0.0, now - timestamp)
    
    if half_life <= 0:
        return DecayResult(0.0, False, delta_t)
        
    decay_factor = math.pow(0.5, (delta_t / half_life))
    current_confidence = initial_confidence * decay_factor
    
    return DecayResult(
        current_confidence=round(current_confidence, 4),
        is_valid=current_confidence >= threshold,
        delta_t=round(delta_t, 2)
    )

def get_decay_telemetry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Generates telemetry for a memory entry's decay state."""
    res = calculate_decay(
        entry.get('confidence', 0.0),
        entry.get('timestamp', 0.0),
        entry.get('decay_half_life_seconds', 86400.0)
    )
    return {
        "confidence": res.current_confidence,
        "is_valid": res.is_valid,
        "age_seconds": res.delta_t
    }