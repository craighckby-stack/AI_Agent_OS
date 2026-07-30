# AI Agent OS: Core Architecture & Kernel Specification

## Overview
This repository implements a lightweight, modular **Local Agent Kernel**. It is designed for high-performance execution in constrained environments (Termux, Colab, or local edge devices) without cloud-native dependencies.

## System Architecture

### 1. Environment Controller (`env_loader.py`)
- **Role**: Bootstraps the kernel environment.
- **Functionality**: Parses `.env` files, expands nested variables (`${VAR}`), and ensures system-wide configuration parity before kernel initialization.

### 2. Execution Kernel (`kernel.py`)
- **Role**: The central orchestration loop.
- **Execution Flow**:
  1. **Registry Discovery**: Scans `modules/*/README.md` to dynamically map capabilities.
  2. **Routing**: Tries LLM-based intent classification (Gemini -> OpenAI -> DeepSeek -> Local) with a keyword-based fallback.
  3. **Memory Layer**: Uses `memory.json` as a persistent cache for module outputs, gated by confidence scores (default: 90%).
  4. **Execution**: Invokes module-specific `run.sh` scripts in a sandboxed process.

### 3. LLM Interface Layer (`llm_router.py`)
- **Role**: Intelligent intent routing.
- **Design**: Implements a fail-fast provider chain. If an API key is missing or a request times out (10s limit), it gracefully degrades to the next provider in the stack.

## Development Guidelines
- **Zero-Leak Policy**: All module executions are isolated via subprocesses.
- **Extensibility**: To add a new capability, create a new directory in `/modules` with a `README.md` (defining `name` and `purpose`) and a `run.sh` script.
- **Memory Integrity**: The memory layer treats stored data as 'evidence, not truth'. Always verify confidence scores before relying on cached results.

## Operational Context
This project is designed to be compatible with the `AI_Agent_OS` design patterns, ensuring that local agents can operate autonomously while maintaining a traceable, auditable execution history.