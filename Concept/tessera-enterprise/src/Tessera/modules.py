"""
Tessera module registry.

Discovers modules under modules/, builds the routing table, and manages
intent-clustered cache keys. Integrates with the Diagnostic Integrity architecture
to provide real-time health telemetry for module discovery and execution.

Module contract:
    Each module lives at modules/<name>/ and contains:
      - README.md declaring name, purpose, and optionally cluster_key
      - run.sh (or any executable) that reads AI_AGENT_REQUEST env var
        and writes its result to stdout
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from tessera.cache import Cache
from tessera.diagnostic_utils_core import generate_telemetry_metadata
from tessera.diagnostic_engine_utils import execute_check_with_telemetry

@dataclass
class ModuleSpec:
    """Specification for a Tessera module, parsed from its README.md."""

    name: str
    purpose: str
    cluster_key: str = "request"  # static | request | extract:image | extract:url
    path: Path = field(default_factory=Path)


DEFAULT_KEYWORD_TABLE: Dict[str, str] = {
    "sky": "sky_colour",
    "colour": "sky_colour",
    "color": "sky_colour",
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
    "calculate": "calculator",
    "compute": "calculator",
}


class ModuleRegistry:
    """
    Discovers and manages modules with integrated diagnostic telemetry.
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

    def check_registry_integrity(self) -> Dict[str, Any]:
        """Performs a diagnostic health check on the module registry."""
        def _check_all():
            self.discover()
            return len(self._modules) > 0
        
        passed, duration = execute_check_with_telemetry(_check_all, "module_registry_integrity")
        return {
            "passed": passed,
            "duration_ms": duration,
            "telemetry": generate_telemetry_metadata(),
            "module_count": len(self._modules)
        }

    def _parse_readme(self, readme_path: Path) -> Optional[ModuleSpec]:
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
        if not self._modules:
            self.discover()
        return self._modules.get(name)

    def names(self) -> list[str]:
        if not self._modules:
            self.discover()
        return list(self._modules.keys())

    def describe(self) -> Dict[str, Dict[str, str]]:
        if not self._modules:
            self.discover()
        return {name: {"purpose": spec.purpose} for name, spec in self._modules.items()}

    def cache_key(self, module_name: str, request: str) -> str:
        spec = self.get(module_name)
        if not spec:
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
            req_hash = hashlib.md5(request.lower().strip().encode()).hexdigest()[:10]
            return f"{module_name}::{req_hash}"

        req_hash = hashlib.md5(request.lower().strip().encode()).hexdigest()[:10]
        return f"{module_name}::{req_hash}"

    def _extract_cluster_token(self, strategy: str, request: str) -> Optional[str]:
        if strategy == "extract:image":
            m = re.search(r"([\w./-]+\.(?:jpg|jpeg|png|webp|bmp|gif))", request, re.IGNORECASE)
            if m:
                return Path(m.group(1)).name.lower()
        elif strategy == "extract:url":
            m = re.search(r"(https?://[^\s]+)", request, re.IGNORECASE)
            if m:
                return m.group(1).lower()
        return None

    def should_store_request(self, module_name: str) -> bool:
        spec = self.get(module_name)
        if not spec:
            return True
        return spec.cluster_key == "request"

    def lookup_cached_module(
        self, request: str, cache: Cache
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        if not self._modules:
            self.discover()

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

        req_hash = hashlib.md5(request.lower().strip().encode()).hexdigest()[:10]
        for name, spec in self._modules.items():
            if spec.cluster_key != "request":
                continue
            cache_key = f"{name}::{req_hash}"
            cached = cache.get(cache_key)
            if cached and cached.get("confidence", 0) >= 90:
                if cached.get("request") == request:
                    return name, cached, cache_key

        for name, spec in self._modules.items():
            if spec.cluster_key != "static":
                continue
            cache_key = name
            cached = cache.get(cache_key)
            if cached and cached.get("confidence", 0) >= 90:
                return name, cached, cache_key

        return None, None, None

    def execute(self, module_name: str, request: str, timeout: int = 180) -> Tuple[str, bool]:
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
