"""Shared pytest fixtures."""
import shutil
import tempfile
from pathlib import Path

import pytest

from tessera.cache import FileCache
from tessera.config import TesseraConfig
from tessera.kernel import Kernel
from tessera.modules import ModuleRegistry


@pytest.fixture
def tmp_cache_dir(tmp_path: Path) -> Path:
    """A temporary directory for cache files."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    yield cache_dir
    shutil.rmtree(cache_dir, ignore_errors=True)


@pytest.fixture
def file_cache(tmp_cache_dir: Path) -> FileCache:
    """A FileCache instance backed by a temp directory."""
    return FileCache(dir_path=tmp_cache_dir)


@pytest.fixture
def modules_dir(tmp_path: Path) -> Path:
    """A temporary modules directory with one trivial test module."""
    mod_dir = tmp_path / "modules" / "echo"
    mod_dir.mkdir(parents=True)
    (mod_dir / "README.md").write_text(
        "name: echo\npurpose: Echoes the request back to the user\ncluster_key: request\n"
    )
    (mod_dir / "run.sh").write_text(
        "#!/bin/bash\necho \"You said: $AI_AGENT_REQUEST\"\n"
    )
    (mod_dir / "run.sh").chmod(0o755)
    return tmp_path / "modules"


@pytest.fixture
def config(tmp_path: Path, modules_dir: Path) -> TesseraConfig:
    """A TesseraConfig pointed at temp dirs, with no LLM keys (keyword-only mode)."""
    return TesseraConfig(
        gemini_api_key="",
        openai_api_key="",
        deepseek_api_key="",
        cache_dir=str(tmp_path / "cache"),
        modules_dir=str(modules_dir),
        default_fallback_module="echo",
    )


@pytest.fixture
def kernel(config: TesseraConfig) -> Kernel:
    """A Kernel instance configured for testing (keyword-only, temp dirs)."""
    return Kernel(config=config)
