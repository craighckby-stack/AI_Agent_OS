#!/usr/bin/env python3
import json
from pathlib import Path

RELAY_DIR = Path(__file__).parent / ".relay"
MANIFEST = RELAY_DIR / "manifest.json"

def init_relay():
    RELAY_DIR.mkdir(parents=True, exist_ok=True)
    if not MANIFEST.exists():
        MANIFEST.write_text(json.dumps([], indent=2))
    print("[1_plan.py] Relay initialized. LLM would decide what 2.sh needs to do here.")

if __name__ == "__main__":
    init_relay()
