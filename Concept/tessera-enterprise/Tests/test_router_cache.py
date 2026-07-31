"""Tests for the router cache (caches routing decisions)."""
import pytest

from tessera.cache import FileCache
from tessera.router_cache import RouterCache


def test_router_cache_miss_returns_none(file_cache: FileCache):
    """Router cache miss should return None."""
    rc = RouterCache(cache=file_cache)
    assert rc.get_decision("any request") is None


def test_router_cache_set_then_get(file_cache: FileCache):
    """Set then get should return the cached module name."""
    rc = RouterCache(cache=file_cache)
    rc.set_decision("what is the sky color", "sky_colour")
    assert rc.get_decision("what is the sky color") == "sky_colour"


def test_router_cache_normalizes_request(file_cache: FileCache):
    """The router cache should normalize request (case, whitespace)."""
    rc = RouterCache(cache=file_cache)
    rc.set_decision("What Is The Sky", "sky_colour")
    # Same words, different case/whitespace → same cache slot
    assert rc.get_decision("what is the sky") == "sky_colour"
    assert rc.get_decision("  WHAT  IS  THE  SKY  ") == "sky_colour"


def test_router_cache_different_requests_get_different_slots(file_cache: FileCache):
    """Different requests should not collide."""
    rc = RouterCache(cache=file_cache)
    rc.set_decision("request one", "module_a")
    rc.set_decision("request two", "module_b")
    assert rc.get_decision("request one") == "module_a"
    assert rc.get_decision("request two") == "module_b"
