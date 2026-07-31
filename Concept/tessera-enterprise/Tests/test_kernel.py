"""Tests for the kernel's cache-before-router behavior."""
import pytest

from tessera.kernel import Kernel


def test_kernel_first_run_is_cache_miss(kernel: Kernel):
    """First run of any request should execute the module (cache miss)."""
    result = kernel.run("hello world")
    assert result.cache_hit is False
    assert result.module == "echo"
    assert "You said: hello world" in result.result


def test_kernel_second_run_is_cache_hit(kernel: Kernel):
    """Second run of the same request should hit the cache (0 LLM calls)."""
    # First run — populates cache
    kernel.run("hello world")
    # Second run — should hit cache
    result = kernel.run("hello world")
    assert result.cache_hit is True
    assert result.routed_via == "cache"
    assert "You said: hello world" in result.result


def test_kernel_different_requests_get_different_cache_slots(kernel: Kernel):
    """Different requests should not share cache entries."""
    kernel.run("first request")
    result = kernel.run("second request")
    assert result.cache_hit is False
    assert "You said: second request" in result.result


def test_kernel_cache_before_router_does_not_call_llm(kernel: Kernel):
    """On a cache hit, the router should NOT be called.

    We verify this by checking that routed_via == 'cache' (not 'llm:*').
    """
    kernel.run("cache me")
    result = kernel.run("cache me")
    assert result.routed_via == "cache"
    assert "llm:" not in result.routed_via


def test_kernel_result_contains_elapsed_time(kernel: Kernel):
    """The result should include a non-negative elapsed time."""
    result = kernel.run("timing test")
    assert result.elapsed_s >= 0
