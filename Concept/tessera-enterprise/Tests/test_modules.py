"""Tests for the module registry: discovery, cache keys, execution with diagnostic telemetry integration."""
import pytest
from typing import Dict, Any
from tessera.modules import ModuleRegistry
from Tessera.diagnostic_utils_core import generate_telemetry_metadata

# Header: Module Registry Diagnostic Test Suite
# Role: Validates registry integrity and diagnostic telemetry attachment.
# Integration: Connects to Tessera.diagnostic_utils_core for telemetry verification.

def test_registry_discovers_modules(modules_dir):
    """Registry should find all modules with a README.md."""
    registry = ModuleRegistry(modules_dir=modules_dir)
    registry.discover()
    assert "echo" in registry.names()


def test_registry_get_returns_spec(modules_dir):
    """get() should return the ModuleSpec for a known module."""
    registry = ModuleRegistry(modules_dir=modules_dir)
    spec = registry.get("echo")
    assert spec is not None
    assert spec.name == "echo"
    assert spec.cluster_key == "request"


def test_registry_get_unknown_module_returns_none(modules_dir):
    """get() should return None for unknown modules."""
    registry = ModuleRegistry(modules_dir=modules_dir)
    assert registry.get("nonexistent") is None


def test_cache_key_request_strategy(modules_dir):
    """cluster_key=request should produce per-phrasing slots."""
    registry = ModuleRegistry(modules_dir=modules_dir)
    key1 = registry.cache_key("echo", "hello")
    key2 = registry.cache_key("echo", "world")
    key3 = registry.cache_key("echo", "hello")
    assert key1 != key2
    assert key1 == key3
    assert key1.startswith("echo::")


def test_cache_key_static_strategy(tmp_path):
    """cluster_key=static should produce one slot per module."""
    mod_dir = tmp_path / "modules" / "static_mod"
    mod_dir.mkdir(parents=True)
    (mod_dir / "README.md").write_text(
        "name: static_mod\npurpose: Always returns the same answer\ncluster_key: static\n"
    )
    (mod_dir / "run.sh").write_text("#!/bin/bash\necho 'static result'\n")
    (mod_dir / "run.sh").chmod(0o755)

    registry = ModuleRegistry(modules_dir=tmp_path / "modules")
    key1 = registry.cache_key("static_mod", "anything")
    key2 = registry.cache_key("static_mod", "something else")
    assert key1 == key2 == "static_mod"


def test_cache_key_extract_image_strategy(tmp_path):
    """cluster_key=extract:image should produce one slot per image filename."""
    mod_dir = tmp_path / "modules" / "img_mod"
    mod_dir.mkdir(parents=True)
    (mod_dir / "README.md").write_text(
        "name: img_mod\npurpose: Image analysis\ncluster_key: extract:image\n"
    )
    (mod_dir / "run.sh").write_text("#!/bin/bash\necho 'img result'\n")
    (mod_dir / "run.sh").chmod(0o755)

    registry = ModuleRegistry(modules_dir=tmp_path / "modules")
    key1 = registry.cache_key("img_mod", "analyze photo.jpg")
    key2 = registry.cache_key("img_mod", "what colors are in photo.jpg")
    assert key1 == key2 == "img_mod::cluster::photo.jpg"

    key3 = registry.cache_key("img_mod", "analyze other.png")
    assert key3 != key1


def test_execute_returns_stdout(modules_dir):
    """execute() should return (stdout, True) on success."""
    registry = ModuleRegistry(modules_dir=modules_dir)
    stdout, ok = registry.execute("echo", "test message")
    assert ok is True
    assert "test message" in stdout


def test_execute_unknown_module_returns_error(modules_dir):
    """execute() should return (error_message, False) for unknown modules."""
    registry = ModuleRegistry(modules_dir=modules_dir)
    stdout, ok = registry.execute("nonexistent", "test")
    assert ok is False
    assert "not found" in stdout


def test_registry_diagnostic_telemetry():
    """Validates that registry operations can attach diagnostic telemetry metadata."""
    telemetry = generate_telemetry_metadata()
    assert "timestamp" in telemetry
    assert "version" in telemetry
    assert telemetry["version"] == "1.0.0-DIAGNOSTIC-AWARE"