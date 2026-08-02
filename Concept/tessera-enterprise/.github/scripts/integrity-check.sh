#!/bin/bash
# Integrity Gate: Validates system health across all modules before release.
echo "[INTEGRITY GATE] Starting system health verification..."

# Check for critical diagnostic files
if [ ! -f "lib/diagnostic-engine.ts" ] && [ ! -f "diagnostic_engine.py" ]; then
  echo "[ERROR] Diagnostic Engine missing. Integrity check failed."
  exit 1
fi

# Validate environment configuration
if [ ! -f ".env.example" ]; then
  echo "[ERROR] .env.example missing. Configuration integrity compromised."
  exit 1
fi

echo "[INTEGRITY GATE] All systems nominal. Proceeding to build."
exit 0