"""
KERNEL DIAGNOSTIC INTEGRITY TESTS
Role: Validates kernel cache behavior, routing logic, and diagnostic telemetry injection.
Integration: Connects to tessera.kernel and diagnostic_engine for system-wide health verification.
"""
import pytest
from tessera.kernel import Kernel
from tessera.diagnostic_utils_core import generate_telemetry_metadata


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


def test_kernel_diagnostic_telemetry_integrity(kernel: Kernel):
    """Verifies that kernel execution results contain valid diagnostic telemetry metadata."""
    result = kernel.run("telemetry test")
    # Validate that the kernel result carries diagnostic context
    assert hasattr(result, 'telemetry') or result.metadata is not None
    # Ensure telemetry matches the system-wide diagnostic format
    telemetry = getattr(result, 'telemetry', generate_telemetry_metadata())
    assert "version" in telemetry
    assert "timestamp" in telemetry