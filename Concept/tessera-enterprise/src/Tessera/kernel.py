"""
Tessera kernel — the central execution loop.

Responsibilities:
    1. Check result cache (intent-clustered) BEFORE calling the router.
    2. On cache miss, check router cache (caches routing decisions).
    3. On router cache miss, call LLM router (or keyword fallback).
    4. Execute the chosen module via subprocess.
    5. Cache successful results. Never cache failures.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from tessera.cache import Cache, FileCache
from tessera.config import TesseraConfig
from tessera.exceptions import (
    CacheMiss,
    KernelError,
    ModuleFailed,
    NoModuleMatched,
)
from tessera.modules import ModuleRegistry
from tessera.router import LLMRouter, Router
from tessera.router_cache import RouterCache

logger = logging.getLogger("tessera.kernel")


@dataclass
class KernelResult:
    """The result of a single kernel.run() invocation."""

    request: str
    module: str
    result: str
    routed_via: str
    cache_key: str
    cache_hit: bool
    router_cache_hit: bool
    elapsed_s: float
    llm_tokens_in: int = 0
    llm_tokens_out: int = 0

    def __str__(self) -> str:
        tag = "cache-hit" if self.cache_hit else (
            "router-cache-hit" if self.router_cache_hit else "executed"
        )
        return (
            f"[{tag} — {self.module}, routed via {self.routed_via}]\n"
            f"Result: {self.result}\n"
            f"(elapsed={self.elapsed_s * 1000:.1f}ms, cache_key={self.cache_key})"
        )


class Kernel:
    """
    The Tessera kernel. Orchestrates routing, caching, and module execution.

    Usage:
        kernel = Kernel()
        result = kernel.run("what colour is the sky")
        print(result.result)
    """

    def __init__(
        self,
        config: Optional[TesseraConfig] = None,
        cache: Optional[Cache] = None,
        router: Optional[Router] = None,
        router_cache: Optional[RouterCache] = None,
        registry: Optional[ModuleRegistry] = None,
    ) -> None:
        self.config = config or TesseraConfig.from_env()
        self.cache = cache or FileCache(dir_path=self.config.cache_dir)
        self.router = router or LLMRouter(config=self.config)
        self.router_cache = router_cache or RouterCache(cache=self.cache)
        self.registry = registry or ModuleRegistry(modules_dir=self.config.modules_dir)

    def run(self, request: str) -> KernelResult:
        """Process a user request through the full kernel pipeline."""
        start = time.monotonic()

        # ── Phase 1: Result cache lookup (intent-clustered) ─────────────
        module_name, cached_entry, cache_key = self.registry.lookup_cached_module(
            request, self.cache
        )
        if cached_entry is not None:
            elapsed = time.monotonic() - start
            return KernelResult(
                request=request,
                module=module_name,
                result=cached_entry["result"],
                routed_via="cache",
                cache_key=cache_key,
                cache_hit=True,
                router_cache_hit=False,
                elapsed_s=elapsed,
            )

        # ── Phase 2: Router cache lookup ────────────────────────────────
        router_cache_hit = False
        cached_module = self.router_cache.get_decision(request)
        if cached_module and cached_module in self.registry.names():
            module_name = cached_module
            routed_via = "router-cache"
            router_cache_hit = True
        else:
            # ── Phase 3: LLM router (or keyword fallback) ───────────────
            module_name, routed_via = self.router.route(
                request, self.registry.describe()
            )
            if module_name is None:
                module_name = self.config.default_fallback_module
                routed_via = "default-fallback"
            # Cache the routing decision
            self.router_cache.set_decision(request, module_name)

        # ── Phase 4: Re-check result cache after routing ────────────────
        # (Defensive: handles race conditions where another process populated
        # the cache between our pre-router check and now.)
        cache_key = self.registry.cache_key(module_name, request)
        cached_entry = self.cache.get(cache_key)
        if cached_entry and cached_entry.get("confidence", 0) >= self.config.cache_confidence_threshold:
            elapsed = time.monotonic() - start
            return KernelResult(
                request=request,
                module=module_name,
                result=cached_entry["result"],
                routed_via=routed_via,
                cache_key=cache_key,
                cache_hit=True,
                router_cache_hit=router_cache_hit,
                elapsed_s=elapsed,
            )

        # ── Phase 5: Execute the module ─────────────────────────────────
        result_text, ok = self.registry.execute(module_name, request)
        if not ok:
            raise ModuleFailed(module_name=module_name, message=result_text)

        # ── Phase 6: Cache the successful result ────────────────────────
        # Never cache failures — a transient 429 or network blip would
        # otherwise poison the cache and every future request for that
        # query would return the error forever.
        self.cache.set(
            cache_key,
            {
                "result": result_text,
                "confidence": 99,
                "last_verified": time.strftime("%Y-%m-%d %H:%M:%S"),
                "request": request if self.registry.should_store_request(module_name) else None,
            },
        )

        elapsed = time.monotonic() - start
        return KernelResult(
            request=request,
            module=module_name,
            result=result_text,
            routed_via=routed_via,
            cache_key=cache_key,
            cache_hit=False,
            router_cache_hit=router_cache_hit,
            elapsed_s=elapsed,
        )
