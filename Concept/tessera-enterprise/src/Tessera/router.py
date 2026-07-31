"""
Tessera LLM router.

Multi-provider LLM interface with fail-fast fallback:
    Gemini → OpenAI → DeepSeek → Local → keyword fallback

If no provider keys are configured, the router falls back to keyword
routing using the module registry's keyword table.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Callable, Dict, Optional, Tuple

from tessera.config import TesseraConfig

logger = logging.getLogger("tessera.router")

TIMEOUT = 10  # seconds per provider call


class Router:
    """Router interface. Implementations pick a module for a given request."""

    def route(self, request: str, registry: Dict[str, Dict[str, str]]) -> Tuple[Optional[str], str]:
        """Return (module_name, routed_via) or (None, 'unrouted')."""
        raise NotImplementedError


class LLMRouter(Router):
    """
    Multi-provider LLM router with keyword fallback.

    Usage:
        router = LLMRouter(config=TesseraConfig.from_env())
        module, via = router.route("what colour is the sky", registry_dict)
    """

    def __init__(self, config: TesseraConfig) -> None:
        self.config = config
        self.providers: list[Tuple[str, Callable[[str], Optional[str]]]] = self._build_providers()

    def _build_providers(self) -> list[Tuple[str, Callable[[str], Optional[str]]]]:
        """Build the provider list based on configured API keys."""
        providers = []
        if self.config.gemini_api_key:
            providers.append(("gemini", self._try_gemini))
        if self.config.openai_api_key:
            providers.append(("openai", self._try_openai))
        if self.config.deepseek_api_key:
            providers.append(("deepseek", self._try_deepseek))
        # Local LLM is always attempted as a last-resort LLM (it may not be running)
        providers.append(("local", self._try_local))
        return providers

    def route(self, request: str, registry: Dict[str, Dict[str, str]]) -> Tuple[Optional[str], str]:
        """Route the request to a module via LLM, falling back to keywords."""
        if not self.providers:
            # No LLM available — straight to keyword fallback
            return self._keyword_fallback(request)

        prompt = self._build_prompt(request, registry)
        for name, fn in self.providers:
            try:
                raw = fn(prompt)
            except Exception as e:
                logger.debug(f"Provider {name} raised: {e}")
                continue
            if raw is None:
                continue
            module = self._extract_module(raw)
            if module and module in registry:
                return module, f"llm:{name}"

        return self._keyword_fallback(request)

    def _keyword_fallback(self, request: str) -> Tuple[Optional[str], str]:
        """Match the request against the keyword table."""
        from tessera.modules import DEFAULT_KEYWORD_TABLE
        lowered = request.lower()
        for keyword, module_name in DEFAULT_KEYWORD_TABLE.items():
            if keyword in lowered:
                return module_name, "keyword-fallback"
        return None, "unrouted"

    def _build_prompt(self, request: str, registry: Dict[str, Dict[str, str]]) -> str:
        """Build the LLM prompt for routing decisions."""
        modules_desc = "\n".join(
            f"- {name}: {meta['purpose']}" for name, meta in registry.items()
        )
        return (
            "You are the routing layer of a local agent kernel. Given a user "
            "request, choose exactly one module from the list below that should "
            "handle it. Respond with ONLY a JSON object of the form "
            '{"module": "<name>"} and nothing else. If nothing fits, respond '
            '{"module": null}.\n\n'
            f"Available modules:\n{modules_desc}\n\n"
            f"Request: {request}"
        )

    def _extract_module(self, text: str) -> Optional[str]:
        """Parse the LLM's response to extract the module name."""
        try:
            cleaned = text.strip().strip("`").replace("json\n", "", 1).strip()
            data = json.loads(cleaned)
            return data.get("module")
        except (json.JSONDecodeError, AttributeError):
            return None

    # ── Provider implementations ───────────────────────────────────────

    def _post_json(self, url: str, headers: Dict[str, str], payload: dict) -> Optional[dict]:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            logger.debug(f"Request failed: {e}")
            return None

    def _try_gemini(self, prompt: str) -> Optional[str]:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={self.config.gemini_api_key}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        data = self._post_json(url, {"Content-Type": "application/json"}, payload)
        if not data:
            return None
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return None

    def _try_openai(self, prompt: str) -> Optional[str]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.openai_api_key}",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
        }
        data = self._post_json(url, headers, payload)
        if not data:
            return None
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return None

    def _try_deepseek(self, prompt: str) -> Optional[str]:
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.deepseek_api_key}",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
        }
        data = self._post_json(url, headers, payload)
        if not data:
            return None
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return None

    def _try_local(self, prompt: str) -> Optional[str]:
        """Try a local LLM server (Ollama, LM Studio, etc.)."""
        payload = {
            "model": self.config.local_llm_model,
            "prompt": prompt,
            "stream": False,
        }
        data = self._post_json(
            self.config.local_llm_url,
            {"Content-Type": "application/json"},
            payload,
        )
        if not data:
            return None
        return data.get("response")
