<!-- 
  AI AGENT OS: MASTER ARCHITECTURE SPECIFICATION
  Role: Defines the kernel lifecycle, diagnostic protocols, and module integration standards.
  Connected to: src/lib/diagnostic-engine.ts, env_loader.py, kernel.py
-->

# AI Agent OS: Core Architecture & Kernel Specification

## Overview
This repository implements a lightweight, modular **Local Agent Kernel**. It is designed for high-performance execution in constrained environments (Termux, Colab, or local edge devices) without cloud-native dependencies. The system is built on a fail-fast, provider-agnostic routing architecture.

## System Architecture

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

### 3. System Integrity & Diagnostic Engine
- **Role**: Validates kernel integrity and memory persistence layers.
- **Implementation**: See `src/lib/diagnostic-engine.ts` for the TypeScript-based diagnostic suite.
- **Checks**: 
  - `env_loader`: Validates variable expansion.
  - `memory_persistence`: Verifies read/write access to `memory.json`.
  - `module_registry`: Ensures all `run.sh` scripts are executable.

## Kernel Lifecycle & Evolution
- **Zero-Leak Policy**: All module executions are isolated via subprocesses. No state leakage occurs between the kernel and the module execution environment.
- **Memory Integrity**: The memory layer treats stored data as 'evidence, not truth'. Always verify confidence scores before relying on cached results.
- **Dynamic Registry**: Adding a new capability is as simple as creating a new directory in `/modules` with a `README.md` and a `run.sh` script.

## Diagnostic & Maintenance
- **Environment Debugging**: Use the `load_env()` utility to verify variable expansion before kernel execution.
- **Routing Transparency**: The kernel outputs the routing method (e.g., `llm:gemini` vs `keyword-fallback`) for every request to facilitate auditing.
- **Memory Purge**: To reset the agent's learned state, simply delete `memory/local/memory.json`.

## Security & Compliance
- **PII Sanitization**: All logs and memory dumps are processed through `Git-Secret-PII-Sanitizer` before persistence to ensure no sensitive credentials leak into the local history.

## Operational Context
This project is designed to be compatible with the `AI_Agent_OS` design patterns, ensuring that local agents can operate autonomously while maintaining a traceable, auditable execution history.