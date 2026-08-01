<!--
==============================================================================
ARCHITECTURAL SYSTEM HEADER: SUPREME EXECUTION & WALKTHROUGH CONTROLLER
==============================================================================
Role: System Walkthrough & Execution Flow Documentation
System Context: This document serves as the authoritative guide to the Local
                Agent Kernel's operational mechanics. It details the step-by-step
                lifecycle of a request, the routing fallback chain, the memory
                subsystem, and the diagnostic governance layer.
Integrations:
  - kernel.py: Implements the execution loop detailed herein.
  - llm_router.py: Implements the multi-provider fallback routing chain.
  - env_loader.py: Bootstraps the environment with Recursive Expansion & Fail-Fast logic.
  - env_validation_schema.py: Enforces manifest-driven integrity constraints.
  - memory/local/memory.json: Persists the flat-file execution memory.
  - src/core/diagnostic_engine.py: System health and integrity verification engine.
  - src/utils/diagnostic_gatekeeper.py: Policy enforcement for system health.
  - VERIFICATION_REGISTRY: Active diagnostic tracking block.
==============================================================================
-->

# What this actually does

A plain walkthrough of the mechanism, no setup steps. If README.md is "how to run it," this is "what happens when you do."

## 📊 System Execution Flow Map

```
+-----------------------------------------------------------------------+
|                           USER REQUEST                                |
|             e.g., "what colour is the sky"                            |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                 BOOTSTRAP & MANIFEST-DRIVEN VALIDATION                |
|      Loads .env, runs Recursive Expansion, validates via Schema        |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                       DIAGNOSTIC INTEGRITY GATE                       |
|             Verifies Kernel, Memory, and Registry Health              |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                       REGISTRY SCANNER & BUILDER                      |
|             Scans modules/*/README.md to build registry               |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                       LLM ROUTING FALLBACK CHAIN                      |
|     Gemini -> OpenAI -> DeepSeek -> Local (Ollama) -> Keywords        |
+-----------------------------------------------------------------------+
                                   |
                                   +---> [Module Selected]
                                   |
                                   v
+-----------------------------------------------------------------------+
|                       EVIDENCE-BASED MEMORY CHECK                     |
|         Reads memory.json, verifies confidence >= 90% & TTL           |
+-----------------------------------------------------------------------+
         |                                           |
     [HIT]                                       [MISS]
         |                                           |
         v                                           v
+------------------+                       +----------------------------+
|  RETURN CACHED   |                       |   EXECUTE MODULE SANDBOX   |
|     RESULT       |                       |       Runs run.sh          |
+------------------+                       +----------------------------+
         |                                           |
         |                                           v
         |                                 +----------------------------+
         |                                 |    WRITE TO MEMORY FILE    |
         |                                 |  Saves result & confidence |
         |                                 +----------------------------+
         |                                           |
         +-------------------+-----------------------+
                             |                                           
                             v
+-----------------------------------------------------------------------+
|                   ENTROPY-BASED MEMORY PRUNING                        |
|        Evaluates state decay and prunes low-confidence nodes          |
+-----------------------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------------------+
|                            FINAL OUTPUT                               |
|             Prints result, routing path, and elapsed time             |
+-----------------------------------------------------------------------+
```

## The short version

You type a request. The kernel performs a diagnostic integrity check, decides which module answers it, checks if it's already answered that exact thing before, and either reuses the old answer or runs the module fresh. Either way you get a result, and the system prunes its memory to maintain peak performance.

---

## 🧠 The Entropy Protocol

To prevent memory bloat and ensure high-fidelity retrieval, the system implements an **Entropy-Based Pruning Strategy**. Every memory node is assigned a decay coefficient based on its usage frequency and confidence score. During the final stage of the execution flow, the `MemoryDecayEngine` identifies and removes nodes that fall below the `MEMORY_PRUNING_THRESHOLD` defined in the `.env` manifest.

## 🛡️ System Integrity & Compliance Verification

To ensure the kernel remains operational, the system performs a diagnostic check on every boot. This verifies that the `modules/` directory is accessible, the `memory/` file structure is writable, and all environment variables meet the `DiagnosticResult` schema requirements.

### Diagnostic Governance
- **Runtime Integrity:** The `src/core/diagnostic_engine.py` utility executes a deep-check of the kernel state.
- **Verification Hook:** Every boot cycle triggers `run_system_diagnostics()` to validate the environment and persistence layers.
- **Gatekeeping:** The `DiagnosticGatekeeper` evaluates the diagnostic report against the `GATEKEEPER_STRICTNESS` policy. Any failure in the diagnostic suite halts execution to prevent state corruption, adhering to the 'Zero-Leak' architecture patterns.

### Verification Registry
- **Status:** Active
- **Protocol Version:** 1.3.0 (Siphoned-Enhanced)
- **System Health Version:** 2024.Q4.BETA
- **Integrity Hook:** Enabled (via `src/core/diagnostic_engine.py`)
- **Telemetry Engine:** Active (via `src/utils/env_telemetry.py`)

For automated health checks and integration details, refer to the `src/core/` and `src/utils/` directories.