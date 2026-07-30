<!--
==============================================================================
ARCHITECTURAL SYSTEM HEADER: SYSTEM EXECUTION & WALKTHROUGH CONTROLLER
==============================================================================
Role: System Walkthrough & Execution Flow Documentation
System Context: This document serves as the authoritative guide to the Local
                Agent Kernel's operational mechanics. It details the step-by-step
                lifecycle of a request, the routing fallback chain, the memory
                subsystem, and the module contract.
Integrations:
  - kernel.py: Implements the execution loop detailed herein.
  - llm_router.py: Implements the multi-provider fallback routing chain.
  - env_loader.py: Bootstraps the environment variables.
  - memory/local/memory.json: Persists the flat-file execution memory.
  - modules/*: Defines the executable capabilities.
  - lib/diagnostic-engine.ts: System health and integrity verification.
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
|                       BOOTSTRAP & ENV LOADER                          |
|             Loads .env, expands variables, sets API keys              |
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
|                            FINAL OUTPUT                               |
|             Prints result, routing path, and elapsed time             |
+-----------------------------------------------------------------------+
```

## The short version

You type a request. The kernel decides which module answers it, checks if it's already answered that exact thing before, and either reuses the old answer or runs the module fresh. Either way you get a result.

--- 

## System Integrity Check

To ensure the kernel remains operational, the system performs a diagnostic check on every boot. This verifies that the `modules/` directory is accessible and the `memory/` file structure is writable. For automated health checks, refer to `lib/diagnostic-engine.ts`.