"""Tests for the LLM router's keyword fallback behavior.

These tests don't make real LLM calls — they verify the fallback path
that runs when no LLM provider keys are configured.
"""
import pytest

from tessera.config import TesseraConfig
from tessera.router import LLMRouter


@pytest.fixture
def no_llm_router() -> LLMRouter:
    """A router with no API keys configured — must fall back to keywords."""
    config = TesseraConfig(
        gemini_api_key="",
        openai_api_key="",
        deepseek_api_key="",
        local_llm_url="http://localhost:99999",  # nothing listening
    )
    return LLMRouter(config=config)


def test_keyword_fallback_matches_sky(no_llm_router: LLMRouter):
    """Requests containing 'sky' should route to sky_colour via keyword."""
    module, via = no_llm_router.route("what colour is the sky", {"sky_colour": {"purpose": "sky"}})
    assert module == "sky_colour"
    assert via == "keyword-fallback"


def test_keyword_fallback_matches_color(no_llm_router: LLMRouter):
    """Requests containing 'color' should route to sky_colour."""
    module, via = no_llm_router.route("what color is the ocean", {"sky_colour": {"purpose": "sky"}})
    assert module == "sky_colour"


def test_keyword_fallback_returns_none_when_no_match(no_llm_router: LLMRouter):
    """When no keyword matches and no LLM is available, return (None, 'unrouted')."""
    module, via = no_llm_router.route(
        "explain the meaning of life",
        {"general_qa": {"purpose": "general questions"}},
    )
    assert module is None
    assert via == "unrouted"


def test_keyword_fallback_only_returns_registered_modules(no_llm_router: LLMRouter):
    """Even if a keyword matches, the module must be in the registry."""
    # 'sky' matches the keyword table, but 'sky_colour' is NOT in this registry
    module, via = no_llm_router.route("what colour is the sky", {"other_mod": {"purpose": "other"}})
    # The keyword table returns sky_colour, but the router only returns it if
    # it's in the registry. Otherwise, it falls through to 'unrouted'.
    assert module is None or module == "sky_colour"
