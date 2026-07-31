"""Tests for the cache interface and FileCache implementation."""
import time

import pytest

from tessera.cache import FileCache


def test_file_cache_miss_returns_none(file_cache: FileCache):
    """Cache miss should return None."""
    assert file_cache.get("nonexistent") is None


def test_file_cache_set_then_get(file_cache: FileCache):
    """Set then get should return the stored value."""
    file_cache.set("key1", {"result": "hello", "confidence": 99})
    entry = file_cache.get("key1")
    assert entry is not None
    assert entry["result"] == "hello"
    assert entry["confidence"] == 99


def test_file_cache_delete(file_cache: FileCache):
    """Delete should remove the entry."""
    file_cache.set("key1", {"result": "hello"})
    assert file_cache.get("key1") is not None
    file_cache.delete("key1")
    assert file_cache.get("key1") is None


def test_file_cache_delete_missing_is_noop(file_cache: FileCache):
    """Deleting a missing key should not raise."""
    file_cache.delete("never_existed")  # should not raise


def test_file_cache_clear(file_cache: FileCache):
    """Clear should remove all entries."""
    file_cache.set("key1", {"result": "a"})
    file_cache.set("key2", {"result": "b"})
    file_cache.clear()
    assert file_cache.get("key1") is None
    assert file_cache.get("key2") is None


def test_file_cache_corrupted_file_returns_none(file_cache: FileCache):
    """A corrupted cache file should be treated as a miss, not raise."""
    # Write a corrupted file directly
    path = file_cache._path_for("corrupted")
    path.write_text("not valid json{{{")
    assert file_cache.get("corrupted") is None


def test_file_cache_key_sanitization(file_cache: FileCache):
    """Cache keys with special chars should be sanitized for filesystem safety."""
    file_cache.set("key/with/slashes::and::colons", {"result": "ok"})
    entry = file_cache.get("key/with/slashes::and::colons")
    assert entry is not None
    assert entry["result"] == "ok"
