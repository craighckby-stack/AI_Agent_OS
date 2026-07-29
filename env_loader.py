"""
Minimal .env reader — no python-dotenv dependency, keeps things flat.
Reads KEY=VALUE lines from a .env file in the repo root, if one exists.
Real environment variables always win over the file.
"""

import os
from pathlib import Path

ENV_FILE = Path(__file__).parent / ".env"


def load_env() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
