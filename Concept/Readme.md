<!-- 
  AI AGENT OS: MASTER ARCHITECTURE SPECIFICATION
  Role: Defines the kernel lifecycle, diagnostic protocols, and module integration standards.
  Connected to: src/lib/diagnostic-engine.ts, src/lib/zero-leak-sandbox.ts, src/lib/consensus-weighting.ts, env_loader.py, kernel.py, scripts/diagnostic-hook.sh, Concept/consensus-weighting-spec.md
  Status: DIAGNOSTIC-AWARE & ZERO-LEAK COMPLIANT
-->

# AI Agent OS: Core Architecture & Kernel Specification

## Overview
This repository implements a lightweight, modular **Local Agent Kernel**. It is designed for high-performance execution in constrained environments (Termux, Colab, or local edge devices) without cloud-native dependencies. The system is built on a fail-fast, provider-agnostic routing architecture, reinforced by a TypeScript-based diagnostic suite and zero-leak sandboxing.

## System Architecture & Component Topology

```
+-----------------------------------------------------------------+
|                       USER INTERACTION LAYER                    |
+-----------------------------------------------------------------+
                                 |
                                 v
+-----------------------------------------------------------------+
|                         LOCAL KERNEL                            |
|  - env_loader.py (Environment Controller)                       |
|  - kernel.py (Execution & Routing Loop)                         |
+-----------------------------------------------------------------+
        |                        |                        |
        v                        v                        v
+---------------+        +---------------+        +---------------+
|  DIAGNOSTIC   |        |   ZERO-LEAK   |        |   CONSENSUS   |
|    ENGINE     |        |   SANDBOX     |        |   WEIGHTING   |
| (TypeScript)  |        |  (WeakMaps)   |        |  (Multi-Agent)|
+---------------+        +---------------+        +---------------+
```

### 1. Environment Controller (`env_loader.py`)
- **Role**: Bootstraps the kernel environment.
- **Functionality**: Parses `.env` files, expands nested variables (`${VAR}`), and ensures system-wide configuration parity before kernel initialization.

### 2. Execution Kernel (`kernel.py`)
- **Role**: The central orchestration loop.
- **Execution Flow**:
  1. **Registry Discovery**: Scans `modules/*/README.md` to dynamically map capabilities.
  2. **Routing**: Tries LLM-based intent classification (Gemini -> OpenAI -> DeepSeek -> Local) with a keyword-based fallback.
  3. **Memory Layer**: Uses `memory.json` as a persistent cache for module outputs.
  4. **Execution**: Invokes module-specific `run.sh` scripts in a sandboxed process.

### 3. System Integrity & Diagnostic Engine (`src/lib/diagnostic-engine.ts`)
- **Role**: Validates kernel integrity, memory persistence layers, and module registry status.
- **Implementation**: Ported from the Python diagnostic engine to a highly performant TypeScript implementation.
- **Checks**:
  - `env_loader`: Validates variable expansion and configuration parity.
  - `memory_persistence`: Verifies read/write access to `memory.json` and checks for potential memory leaks.
  - `module_registry`: Ensures all `run.sh` scripts are executable and compliant.

### 4. Zero-Leak Sandboxing (`src/lib/zero-leak-sandbox.ts`)
- **Role**: Prevents memory leaks and state contamination during multi-agent execution cycles.
- **Implementation**: Utilizes JavaScript/TypeScript `WeakMap` structures to bind execution contexts to agent instances. This ensures that when an agent is garbage collected, its entire execution memory space is immediately reclaimed by the engine without manual teardown.

### 5. Dynamic Consensus Weighting (`src/lib/consensus-weighting.ts`)
- **Role**: Optimizes multi-agent decision-making by dynamically adjusting agent influence based on historical accuracy and confidence scores.
- **Implementation**: Implements a mathematical weighting algorithm that penalizes high-entropy/low-accuracy outputs while rewarding consistent performance. See [Consensus Weighting Specification](./consensus-weighting-spec.md) for detailed mathematical formulations.

## Diagnostic Governance & Fail-Fast Mandate
- **Diagnostic Integrity Hook**: The kernel utilizes a `runSystemDiagnostics()` hook to verify environment state at runtime.
- **Verification Contract**: Any new module must implement a `diagnostic_check.sh` to be considered 'Kernel-Compliant'.
- **Fail-Fast Policy**: If `runSystemDiagnostics()` returns `CRITICAL_FAILURE`, the kernel will halt execution immediately to prevent state corruption or memory leaks.

## Kernel Lifecycle & Evolution
- **Zero-Leak Policy**: All module executions are isolated via subprocesses or WeakMap-bound sandboxes. No state leakage occurs between the kernel and the module execution environment.
- **Memory Integrity**: The memory layer treats stored data as 'evidence, not truth'. Always verify confidence scores and consensus weights before relying on cached results.
- **Dynamic Registry**: Adding a new capability is as simple as creating a new directory in `/modules` with a `README.md` and a `run.sh` script.

## Diagnostic & Maintenance
- **Environment Debugging**: Use the `load_env()` utility to verify variable expansion before kernel execution.
- **Routing Transparency**: The kernel outputs the routing method (e.g., `llm:gemini` vs `keyword-fallback`) for every request to facilitate auditing.
- **Memory Purge**: To reset the agent's learned state, simply delete `memory/local/memory.json` or invoke the diagnostic cleanup routine.

## Security & Compliance
- **PII Sanitization**: All logs and memory dumps are processed through the `Git-Secret-PII-Sanitizer` before persistence to ensure no sensitive credentials leak into the local history.
- **Sandbox Isolation**: Prevent unauthorized filesystem access by enforcing strict path-boundary checks within the execution sandbox.