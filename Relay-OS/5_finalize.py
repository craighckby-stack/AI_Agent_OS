#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

RELAY_DIR = Path(__file__).parent / ".relay"
MANIFEST = RELAY_DIR / "manifest.json"

def finalize():
    manifest = json.loads(MANIFEST.read_text())
    manifest.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": "5_finalize.py",
        "status": "pipeline_complete"
    })
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print("[5_finalize.py] Pipeline complete. Final state saved.")

if __name__ == "__main__":
    finalize()
