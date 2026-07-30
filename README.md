<!-- 
  ARCHITECTURAL MANIFEST: AI_Agent_OS
  Role: Master Specification & Kernel Integrity Contract
  Siphoned Patterns: craighckby-stack/AI_Agent_OS (Diagnostic Engine)
  Status: OPERATIONAL | Integrity: VERIFIED
-->

# AI Agent OS: Local Kernel

> **SYSTEM STATUS:** Operational
> **CONTROLLER:** DARLEK CANN
> **ARCHITECTURAL MANDATE:** Zero-Cloud Dependency, Flat-File Memory, Multi-Provider LLM Fallback.

## System Health & Verification
To ensure system stability, the kernel utilizes an integrated diagnostic engine (see `lib/diagnostic-engine.ts`). This engine validates:
- **Env Loader**: Configuration integrity.
- **Memory Persistence**: Flat-file state consistency.
- **Module Registry**: Contract-based discovery of execution units.

### Diagnostic Integrity Hook
```typescript
import { runSystemDiagnostics } from './lib/diagnostic-engine';

// Execute diagnostic suite before kernel initialization
const report = await runSystemDiagnostics();
if (report.status !== 'HEALTHY') {
  console.error("[CRITICAL] Kernel Integrity Compromised:", report.checks);
  throw new Error("Kernel Integrity Compromised");
}
```

## Diagnostic Governance
All system modules MUST implement a diagnostic interface. The kernel enforces a 'Fail-Fast' policy: if any critical dependency fails the `runSystemDiagnostics` check, the execution loop is halted to prevent state corruption. This ensures the repository remains in a verifiable, production-ready state at all times.

## System Overview
AI Agent OS is a lightweight, local-first agent kernel designed for execution in constrained environments (Colab, Termux, or local Linux/macOS). It utilizes a modular, contract-based architecture where the kernel acts as a router, memory manager, and execution orchestrator.

## Core Components
- **`kernel.py`**: The central execution loop. Handles request routing, memory lookups, and module invocation.
- **`llm_router.py`**: A resilient multi-provider interface (Gemini/OpenAI/DeepSeek/Local). It implements a fail-fast strategy, falling back to keyword matching if no LLM is available.
- **`env_loader.py`**: A zero-dependency configuration engine that parses `.env` files and expands system variables for the kernel.
- **`modules/`**: A directory of isolated execution units. Each module is defined by a `README.md` (contract) and a `run.sh` (execution script).

## Setup & Deployment

1. **Extraction**:
   ```bash
   tar -xzf agent-os.tar.gz
   cd agent-os
   ```

2. **Configuration**:
   Copy the template and inject your credentials:
   ```bash
   cp .env.example .env
   ```
   *Note: No keys are strictly required. The system defaults to keyword-based routing if API keys are absent.*

3. **Execution**:
   ```bash
   python3 kernel.py "what colour is the sky"
   ```

## Module Lifecycle
To add a new capability, create a directory under `modules/`:
- **`README.md`**: Must contain `name:` and `purpose:` fields. The kernel scans these automatically to build the routing registry.
- **`run.sh`**: The executable script. Output to `stdout` is captured and persisted to `memory/local/memory.json`.

## Memory & Persistence
Memory is stored as a flat JSON file (`memory/local/memory.json`). The kernel treats memory as **evidence, not truth** (Section 5 of Architecture). It validates entries based on confidence scores and expiration timestamps before deciding whether to bypass module execution.

## Security & Integrity
- **Zero-Leak Sandboxing**: Modules execute via `subprocess` with captured output, preventing direct memory access to the kernel.
- **Flat-File Backend**: No external database dependencies. All state is local, ensuring portability across devices.
- **Resilient Routing**: The system prioritizes LLM-based routing but maintains a hard-coded keyword fallback to ensure 100% uptime regardless of network or API availability.

## Development Roadmap
- [ ] Implement `memory/remote` backend for Firebase synchronization.
- [ ] Expand `llm_router` to support local RAG-based context injection.
- [ ] Formalize `run.sh` input/output schemas for stricter type safety.