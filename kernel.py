#!/usr/bin/env python3
"""
ARCHITECTURAL KERNEL — SYSTEM EXECUTION CORE
Role: Orchestrates request routing, module execution, and memory persistence.
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
from typing import Dict, Any, Tuple, Optional

from env_loader import load_env
from llm_router import route_via_llm
from diagnostic_engine import run_system_diagnostics
from lib.kernel_context import KernelContext

# VERIFICATION_REGISTRY: System integrity contract
SYSTEM_HEALTH_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024.10.27"

# Initialize environment and diagnostic hooks
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

class KernelState:
    """Encapsulates system state and registry management."""
    @staticmethod
    def build_registry() -> Dict[str, Any]:
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

    @staticmethod
    def load_memory() -> Dict[str, Any]:
        if not MEMORY_FILE.exists():
            return {}
        try:
            return json.loads(MEMORY_FILE.read_text())
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def save_memory(memory: Dict[str, Any]) -> None:
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        MEMORY_FILE.write_text(json.dumps(memory, indent=2))

class KernelLifecycle:
    """Manages the execution lifecycle and diagnostic gatekeeping."""
    @staticmethod
    def verify_integrity() -> bool:
        diag_report = run_system_diagnostics()
        if diag_report.get('status') != 'HEALTHY':
            print(f"[CRITICAL] Kernel integrity failure: {diag_report.get('status')}")
            return False
        return True

def route_request(request: str, registry: Dict[str, Any]) -> Tuple[Optional[str], str]:
    module, provider = route_via_llm(request, registry)
    if module and module in registry:
        return module, f"llm:{provider}"

    lowered = request.lower()
    for keyword, fallback_module in ROUTING_TABLE.items():
        if keyword in lowered:
            return fallback_module, "keyword-fallback"
    return None, "unrouted"

def execute_module(module_name: str) -> str:
    script = MODULES_DIR / module_name / "run.sh"
    result = subprocess.run(
        ["bash", str(script)], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()

def run(request: str) -> None:
    # Perform diagnostic health check before execution
    if not KernelLifecycle.verify_integrity():
        return

    # Initialize Kernel Context
    ctx = KernelContext(request)
    start = time.monotonic()
    state = KernelState()
    memory = state.load_memory()
    registry = state.build_registry()

    module_name, routed_via = route_request(request, registry)
    if module_name is None:
        print(f"No module matched request: {request!r}")
        return

    cached = memory.get(module_name)
    if cached and cached.get("confidence", 0) >= 90:
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
    state.save_memory(memory)

    elapsed = time.monotonic() - start
    print(f"[memory miss — executed {module_name}, routed via {routed_via}]")
    print(f"Result: {result}")
    print(f"(elapsed={elapsed*1000:.1f}ms, written to memory)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 kernel.py \"<request>\"")
        sys.exit(1)
    run(" ".join(sys.argv[1:]))