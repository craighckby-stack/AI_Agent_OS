"""
Tessera module registry.

Discovers modules under modules/, builds the routing table, and manages
intent-clustered cache keys.

Module contract:
    Each module lives at modules/<name>/ and contains:
      - README.md declaring name, purpose, and optionally cluster_key
      - run.sh (or any executable) that reads AI_AGENT_REQUEST env var
        and writes its result to stdout

Cache key strategies (declared via cluster_key in README.md):
    static         → one slot per module (deterministic output)
    request        → one slot per unique phrasing
    extract:image  → one slot per image filename (semantic cluster)
    extract:url    → one slot per URL (semantic cluster)
    extract:regex:<pattern> → custom extraction (future)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from tessera.cache import Cache


@dataclass
class ModuleSpec:
    """Specification for a Tessera module, parsed from its README.md."""

    name: str
    purpose: str
    cluster_key: str = "request"  # static | request | extract:image | extract:url
    path: Path = field(default_factory=Path)


# Keyword routing table — used when no LLM provider is available.
# Maps lowercase substrings to module names.
DEFAULT_KEYWORD_TABLE: Dict[str, str] = {
    # sky_colour
    "sky": "sky_colour",
    "colour": "sky_colour",
    "color": "sky_colour",
    # pixel_analyzer
    "pixel": "pixel_analyzer",
    "rgb": "pixel_analyzer",
    "analyze image": "pixel_analyzer",
    "image analysis": "pixel_analyzer",
    "color analysis": "pixel_analyzer",
    "colour analysis": "pixel_analyzer",
    "dominant color": "pixel_analyzer",
    "dominant colour": "pixel_analyzer",
    ".jpg": "pixel_analyzer",
    ".png": "pixel_analyzer",
    # calculator
    "calculate": "calculator",
    "compute": "calculator",
    # Note: "what is" is intentionally NOT in the keyword table — it would
    # collide with general questions like "what is the capital of France".
    # The LLM router handles "what is 2+2" vs "what is X" disambiguation.
}


class ModuleRegistry:
    """
    Discovers and manages modules.

    Usage:
        registry = ModuleRegistry(modules_dir="./modules")
        registry.discover()
        spec = registry.get("pixel_analyzer")
        cache_key = registry.cache_key("pixel_analyzer", "analyze sample.jpg")
    """

    def __init__(
        self,
        modules_dir: str | Path = "./modules",
        keyword_table: Optional[Dict[str, str]] = None,
    ) -> None:
        self.modules_dir = Path(modules_dir)
        self.keyword_table = keyword_table or DEFAULT_KEYWORD_TABLE
        self._modules: Dict[str, ModuleSpec] = {}

    def discover(self) -> Dict[str, ModuleSpec]:
        """Scan modules_dir for module folders and parse their README.md specs."""
        self._modules.clear()
        if not self.modules_dir.exists():
            return self._modules
        for readme in sorted(self.modules_dir.glob("*/README.md")):
            spec = self._parse_readme(readme)
            if spec:
                self._modules[spec.name] = spec
        return self._modules

    def _parse_readme(self, readme_path: Path) -> Optional[ModuleSpec]:
        """Parse a module's README.md to extract its spec."""
        try:
            text = readme_path.read_text()
        except OSError:
            return None

        name_match = re.search(r"name:\s*(\S+)", text)
        purpose_match = re.search(r"purpose:\s*(.+)", text)
        cluster_match = re.search(r"cluster_key:\s*(\S+)", text)

        if not name_match:
            return None

        return ModuleSpec(
            name=name_match.group(1),
            purpose=purpose_match.group(1).strip() if purpose_match else "",
            cluster_key=cluster_match.group(1) if cluster_match else "request",
            path=readme_path.parent,
        )

    def get(self, name: str) -> Optional[ModuleSpec]:
        """Return the spec for module `name`, or None."""
        if not self._modules:
            self.discover()
        return self._modules.get(name)

    def names(self) -> list[str]:
        """Return all discovered module names."""
        if not self._modules:
            self.discover()
        return list(self._modules.keys())

    def describe(self) -> Dict[str, Dict[str, str]]:
        """Return a dict suitable for the LLM router's prompt."""
        if not self._modules:
            self.discover()
        return {name: {"purpose": spec.purpose} for name, spec in self._modules.items()}

    # ── Cache key management ───────────────────────────────────────────

    def cache_key(self, module_name: str, request: str) -> str:
        """Compute the cache key for (module, request) based on the module's
        cluster_key strategy."""
        spec = self.get(module_name)
        if not spec:
            # Unknown module — fall back to per-request hashing
            req_hash = hashlib.md5(request.lower().strip().encode()).hexdigest()[:10]
            return f"{module_name}::{req_hash}"

        if spec.cluster_key == "static":
            return module_name

        if spec.cluster_key == "request":
            req_hash = hashlib.md5(request.lower().strip().encode()).hexdigest()[:10]
            return f"{module_name}::{req_hash}"

        if spec.cluster_key.startswith("extract:"):
            token = self._extract_cluster_token(spec.cluster_key, request)
            if token:
                return f"{module_name}::cluster::{token}"
            # No token extracted — fall back to per-request
            req_hash = hashlib.md5(request.lower().strip().encode()).hexdigest()[:10]
            return f"{module_name}::{req_hash}"

        # Unknown strategy — default to per-request
        req_hash = hashlib.md5(request.lower().strip().encode()).hexdigest()[:10]
        return f"{module_name}::{req_hash}"

    def _extract_cluster_token(self, strategy: str, request: str) -> Optional[str]:
        """Extract a stable cluster token from the request based on strategy."""
        if strategy == "extract:image":
            # Match image file paths or URLs
            m = re.search(r"([\w./-]+\.(?:jpg|jpeg|png|webp|bmp|gif))", request, re.IGNORECASE)
            if m:
                return Path(m.group(1)).name.lower()
        elif strategy == "extract:url":
            # Match any URL
            m = re.search(r"(https?://[^\s]+)", request, re.IGNORECASE)
            if m:
                return m.group(1).lower()
        return None

    def should_store_request(self, module_name: str) -> bool:
        """Whether to store the original request in the cache entry.

        For `request` strategy: yes (defensive collision check on lookup).
        For `static` and `extract:*` strategies: no (cache key encodes identity).
        """
        spec = self.get(module_name)
        if not spec:
            return True
        return spec.cluster_key == "request"

    # ── Cache lookup (intent-clustered) ────────────────────────────────

    def lookup_cached_module(
        self, request: str, cache: Cache
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        Scan the cache for an entry matching this request, WITHOUT calling
        the router. This is the cache-before-router optimization.

        Returns (module_name, cached_entry, cache_key) on hit, or
        (None, None, None) on miss.
        """
        if not self._modules:
            self.discover()

        # Try each module's cache key strategy in priority order:
        # 1. extract:* strategies (semantic clusters) — highest value
        # 2. request strategy (per-phrasing)
        # 3. static strategy (one slot per module)

        # 1. Semantic-cluster modules
        for name, spec in self._modules.items():
            if not spec.cluster_key.startswith("extract:"):
                continue
            token = self._extract_cluster_token(spec.cluster_key, request)
            if token is None:
                continue
            cache_key = f"{name}::cluster::{token}"
            cached = cache.get(cache_key)
            if cached and cached.get("confidence", 0) >= 90:
                return name, cached, cache_key

        # 2. Per-request modules
        req_hash = hashlib.md5(request.lower().strip().encode()).hexdigest()[:10]
        for name, spec in self._modules.items():
            if spec.cluster_key != "request":
                continue
            cache_key = f"{name}::{req_hash}"
            cached = cache.get(cache_key)
            if cached and cached.get("confidence", 0) >= 90:
                # Defensive: verify request matches (md5[:10] collisions are
                # vanishingly rare but not impossible)
                if cached.get("request") == request:
                    return name, cached, cache_key

        # 3. Static modules
        for name, spec in self._modules.items():
            if spec.cluster_key != "static":
                continue
            cache_key = name
            cached = cache.get(cache_key)
            if cached and cached.get("confidence", 0) >= 90:
                return name, cached, cache_key

        return None, None, None

    # ── Module execution ───────────────────────────────────────────────

    def execute(self, module_name: str, request: str, timeout: int = 180) -> Tuple[str, bool]:
        """
        Execute the module's run.sh with AI_AGENT_REQUEST set.

        Returns (stdout, ok). On failure, returns (error_message, False)
        instead of raising — the kernel degrades gracefully.
        """
        spec = self.get(module_name)
        if not spec:
            return f"[module {module_name} not found]", False

        script = spec.path / "run.sh"
        if not script.exists():
            return f"[module {module_name} has no run.sh]", False

        env = dict(os.environ)
        env["AI_AGENT_REQUEST"] = request

        try:
            result = subprocess.run(
                ["bash", str(script)],
                capture_output=True,
                text=True,
                check=True,
                env=env,
                timeout=timeout,
            )
            return result.stdout.strip(), True
        except subprocess.CalledProcessError as e:
            err = (e.stderr or "").strip().split("\n")[-1] if e.stderr else f"exit {e.returncode}"
            return f"[module {module_name} failed: {err}]", False
        except subprocess.TimeoutExpired:
            return f"[module {module_name} timed out after {timeout}s]", False
        except OSError as e:
            return f"[module {module_name} os error: {e}]", False
