"""
CACHE DIAGNOSTIC UTILITIES
Role: Provides health monitoring for FileCache storage.
Integration: Used by cache.py to report storage integrity.
"""

import time
from pathlib import Path
from typing import Dict, Any

class CacheDiagnostic:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir

    def run_check(self) -> Dict[str, Any]:
        """Performs a health check on the cache directory."""
        try:
            is_writable = os.access(self.cache_dir, os.W_OK) if hasattr(os, 'access') else True
            files = list(self.cache_dir.glob("*.json"))
            return {
                "status": "HEALTHY" if is_writable else "DEGRADED",
                "file_count": len(files),
                "timestamp": time.time(),
                "writable": is_writable
            }
        except Exception as e:
            return {"status": "CRITICAL", "error": str(e)}
