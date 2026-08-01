"""
Tessera cache interface and FileCache implementation.

The Cache interface is the open-core boundary. The default FileCache is
zero-dependency and ships free. RedisCache (distributed) lives in the
enterprise package.

This module is integrated with the Tessera Enterprise Diagnostic Engine.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

from .cache_diagnostics import CacheDiagnostic

class Cache(Protocol):
    """Cache interface. Any implementation must satisfy this protocol."""

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Return the cached entry for `key`, or None on miss."""
        ...

    def set(self, key: str, value: Dict[str, Any], ttl: int = 0) -> None:
        """Store `value` under `key`. ttl=0 means no expiry."""
        ...

    def delete(self, key: str) -> None:
        """Remove `key` from the cache. No-op if missing."""
        ...

    def clear(self) -> None:
        """Remove all entries. Use with caution."""
        ...


class FileCache:
    """
    Default cache backend. Stores entries as JSON files in a directory.

    Zero dependencies. Suitable for single-process deployments. For
    multi-process or distributed deployments, use RedisCache.
    """

    def __init__(self, dir_path: str | Path) -> None:
        self.dir = Path(dir_path)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.diagnostic = CacheDiagnostic(self.dir)

    def _path_for(self, key: str) -> Path:
        # Sanitize key for filesystem safety
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in key)
        return self.dir / f"{safe}.json"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        path = self._path_for(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            # Check TTL
            expires_at = data.get("_expires_at")
            if expires_at and time.time() > expires_at:
                self.delete(key)
                return None
            return data
        except (json.JSONDecodeError, OSError):
            # Corrupted cache file — treat as miss
            return None

    def set(self, key: str, value: Dict[str, Any], ttl: int = 0) -> None:
        path = self._path_for(key)
        with self._lock:
            entry = {**value}
            if ttl > 0:
                entry["_expires_at"] = time.time() + ttl
            path.write_text(json.dumps(entry, indent=2))

    def delete(self, key: str) -> None:
        path = self._path_for(key)
        with self._lock:
            try:
                path.unlink()
            except FileNotFoundError:
                pass

    def clear(self) -> None:
        with self._lock:
            for path in self.dir.glob("*.json"):
                try:
                    path.unlink()
                except OSError:
                    pass

    def verify_integrity(self) -> Dict[str, Any]:
        """Executes diagnostic check on the cache storage."""
        return self.diagnostic.run_check()