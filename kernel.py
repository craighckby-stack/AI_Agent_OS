#!/usr/bin/env python3
"""
Kernel — the smallest possible implementation of the loop described in
AI_Agent_OS_Architecture.md Section 4 (Execution Flow) and the benchmark
at the end of that document.

Runs identically in a Colab cell or in Termux on-device. No branching
on environment anywhere in this file — that's the point.

Diagnostic Integration: Connects to diagnostic_engine.py for real-time system health monitoring.

Usage:
    python3 kernel.py "what colour is the sky"
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

from env_loader import load_env
from llm_router import route_via_llm
from diagnostic_engine import run_system_diagnostics

load_env()

ROOT = Path(__file__).parent
MODULES_DIR = ROOT / "modules"
MEMORY_FILE = ROOT / "memory" / "local" / "memory.json"

# Last-resort fallback if every LLM provider is unavailable
ROUTING_TABLE = {
    "sky": "sky_colour",
    "colour": "sky_colour",
    "color": "sky_colour",
}


def build_registry() -> dict:
    """Scan modules/*/README.md and pull name + purpose for each module."""
    registry = {}
    for readme in MODULES_DIR.glob("*/README.md"):
        text = readme.read_text()
        name_match = re.search(r"name:\s*(\S+)", text)
        purpose_match = re.search(r"purpose:\s*(.+)", text)
        if name_match:
            registry[name_match.group(1)] = {
                "purpose": purpose_match.group(1).strip() if purpose_match else "",
            }
    return registry


def load_memory() -> dict:
    if not MEMORY_FILE.exists():
        return {}
    return json.loads(MEMORY_FILE.read_text())


def save_memory(memory: dict) -> None:
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))


def route_request(request: str, registry: dict) -> tuple[str | None, str]:
    module, provider = route_via_llm(request, registry)
    if module and module in registry:
        return module, f"llm:{provider}"

    lowered = request.lower()
    for keyword, fallback_module in ROUTING_TABLE.items():
        if keyword in lowered:
            return fallback_module, "keyword-fallback"
    return None, "unrouted"


def check_memory(memory: dict, module_name: str) -> dict | None:
    entry = memory.get(module_name)
    if entry is None or entry.get("confidence", 0) < 90:
        return None
    return entry


def execute_module(module_name: str) -> str:
    script = MODULES_DIR / module_name / "run.sh"
    result = subprocess.run(
        ["bash", str(script)], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def run(request: str) -> None:
    # Perform diagnostic health check before execution
    diag_report = run_system_diagnostics()
    if diag_report.get('status') == 'CRITICAL_FAILURE':
        print(f"[CRITICAL] Kernel integrity failure: {diag_report.get('error')}")
        return

    start = time.monotonic()
    memory = load_memory()
    registry = build_registry()

    module_name, routed_via = route_request(request, registry)
    if module_name is None:
        print(f"No module matched request: {request!r}")
        return

    cached = check_memory(memory, module_name)
    if cached is not None:
        elapsed = time.monotonic() - start
        print(f"[memory hit — no module execution, routed via {routed_via}]")
        print(f"Result: {cached['result']}")
        print(f"(workflow={module_name}, confidence={cached['confidence']}%, elapsed={elapsed*1000:.1f}ms)")
        return

    result = execute_module(module_name)
    memory[module_name] = {
        "result": result,
        "confidence": 99,
        "last_verified": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dependencies": [],
    }
    save_memory(memory)

    elapsed = time.monotonic() - start
    print(f"[memory miss — executed {module_name}, routed via {routed_via}]")
    print(f"Result: {result}")
    print(f"(elapsed={elapsed*1000:.1f}ms, written to memory)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 kernel.py \"<request>\"")
        sys.exit(1)
    run(" ".join(sys.argv[1:]))