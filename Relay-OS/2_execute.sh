#!/bin/bash
exec 2>&1
set -e

echo "[2_execute.sh] Executing system commands..."

# FIX 1: Explicitly export variables so Python subprocess can see them
export NEXTJS_PROJECT_DIR="${NEXTJS_PROJECT_DIR:-./workspace/next-app}"
export BUILD_ID="${BUILD_ID:-$(date +%s)}"

echo "Simulating build for $NEXTJS_PROJECT_DIR (Build ID: $BUILD_ID)"
mkdir -p workspace
echo "Build artifact $BUILD_ID" > workspace/artifact.txt

python3 - << 'EOF'
import json, os, socket, sys
from datetime import datetime, timezone
manifest_path = os.path.join(".relay", "manifest.json")
try:
    with open(manifest_path) as f:
        manifest = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"FATAL: Cannot read relay manifest: {e}")
    sys.exit(1)  # FIX 3 & Improvement 3: Fail loudly on JSON corruption
    
manifest.append({
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "hostname": socket.gethostname(),
    "build_id": os.environ.get("BUILD_ID", "unknown"),
    "step": "2_execute.sh",
    "status": "success",
    "artifact": "workspace/artifact.txt"
})
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)
print("[2_execute.sh] State appended to relay via Python.")
EOF
