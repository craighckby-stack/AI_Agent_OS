"""
Tessera configuration.

Settings are loaded from environment variables (with .env file support
optional — Tessera does not depend on python-dotenv by default). All
settings have sensible defaults so Tessera runs out of the box.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class TesseraConfig:
    """Tessera runtime configuration."""

    # ── LLM providers ──────────────────────────────────────────────────
    gemini_api_key: str = ""
    openai_api_key: str = ""
    deepseek_api_key: str = ""
    local_llm_url: str = "http://localhost:11434/api/generate"
    local_llm_model: str = "llama3.2"

    # ── Cache ──────────────────────────────────────────────────────────
    cache_backend: str = "file"
    cache_dir: str = "./memory/local"
    cache_redis_url: str = ""
    cache_confidence_threshold: int = 90
    cache_ttl: int = 0  # 0 = no expiry

    # ── Router cache ───────────────────────────────────────────────────
    router_cache_enabled: bool = True

    # ── Modules ────────────────────────────────────────────────────────
    modules_dir: str = "./modules"
    default_fallback_module: str = "general_qa"

    # ── Diagnostics ────────────────────────────────────────────────────
    strict_mode: bool = True
    debug_mode: bool = False

    @classmethod
    def from_env(cls, env: Optional[dict] = None) -> "TesseraConfig":
        """Load configuration from environment variables (or a dict)."""
        e = env or os.environ
        return cls(
            gemini_api_key=e.get("GEMINI_API_KEY", ""),
            openai_api_key=e.get("OPENAI_API_KEY", ""),
            deepseek_api_key=e.get("DEEPSEEK_API_KEY", ""),
            local_llm_url=e.get("LOCAL_LLM_URL", "http://localhost:11434/api/generate"),
            local_llm_model=e.get("LOCAL_LLM_MODEL", "llama3.2"),
            cache_backend=e.get("TESSERA_CACHE_BACKEND", "file"),
            cache_dir=e.get("TESSERA_CACHE_DIR", "./memory/local"),
            cache_redis_url=e.get("TESSERA_CACHE_REDIS_URL", ""),
            cache_confidence_threshold=int(e.get("TESSERA_CACHE_CONFIDENCE_THRESHOLD", "90")),
            cache_ttl=int(e.get("TESSERA_CACHE_TTL", "0")),
            router_cache_enabled=e.get("TESSERA_ROUTER_CACHE_ENABLED", "true").lower() in ("true", "1", "yes"),
            modules_dir=e.get("TESSERA_MODULES_DIR", "./modules"),
            default_fallback_module=e.get("TESSERA_DEFAULT_FALLBACK_MODULE", "general_qa"),
            strict_mode=e.get("STRICT_MODE", "true").lower() in ("true", "1", "yes"),
            debug_mode=e.get("DEBUG_MODE", "false").lower() in ("true", "1", "yes"),
        )
