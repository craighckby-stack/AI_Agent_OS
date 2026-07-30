# AI Agent OS: Core Architecture & Kernel Specification

## Overview
This repository implements a lightweight, modular **Local Agent Kernel**. It is designed for high-performance execution in constrained environments (Termux, Colab, or local edge devices) without cloud-native dependencies. The system is built on a fail-fast, provider-agnostic routing architecture.

## System Architecture

### 1. Environment Controller (`env_loader.py`)
- **Role**: Bootstraps the kernel environment.
- **Functionality**: Parses `.env` files, expands nested variables (`${VAR}`), and ensures system-wide configuration parity before kernel initialization. It supports multi-line values and inline comments to maintain compatibility with complex deployment environments.

### 2. Execution Kernel (`kernel.py`)
- **Role**: The central orchestration loop.
- **Execution Flow**:
  1. **Registry Discovery**: Scans `modules/*/README.md` to dynamically map capabilities, ensuring the LLM router always has an up-to-date list of available tools.
  2. **Routing**: Tries LLM-based intent classification (Gemini -> OpenAI -> DeepSeek -> Local) with a keyword-based fallback.
  3. **Memory Layer**: Uses `memory.json` as a persistent cache for module outputs, gated by confidence scores (default: 90%).
  4. **Execution**: Invokes module-specific `run.sh` scripts in a sandboxed process to ensure zero-leak execution.

### 3. LLM Interface Layer (`llm_router.py`)
- **Role**: Intelligent intent routing.
- **Design**: Implements a fail-fast provider chain. If an API key is missing or a request times out (10s limit), it gracefully degrades to the next provider in the stack. This ensures the kernel remains functional even if specific cloud providers are unreachable.

## System Integrity & Evolution
- **Zero-Leak Policy**: All module executions are isolated via subprocesses. No state leakage occurs between the kernel and the module execution environment.
- **Memory Integrity**: The memory layer treats stored data as 'evidence, not truth'. Always verify confidence scores before relying on cached results. 
- **Dynamic Registry**: Adding a new capability is as simple as creating a new directory in `/modules` with a `README.md` (defining `name` and `purpose`) and a `run.sh` script.

## Diagnostic & Maintenance
- **Environment Debugging**: Use the `load_env()` utility to verify variable expansion before kernel execution.
- **Routing Transparency**: The kernel outputs the routing method (e.g., `llm:gemini` vs `keyword-fallback`) for every request to facilitate auditing.
- **Memory Purge**: To reset the agent's learned state, simply delete `memory/local/memory.json`.

## Operational Context
This project is designed to be compatible with the `AI_Agent_OS` design patterns, ensuring that local agents can operate autonomously while maintaining a traceable, auditable execution history. It is optimized for integration with `Git-Secret-PII-Sanitizer` for secure deployment.