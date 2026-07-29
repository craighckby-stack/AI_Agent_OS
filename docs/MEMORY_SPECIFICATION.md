<!--
==============================================================================
ARCHITECTURAL SYSTEM HEADER: EVIDENCE-BASED MEMORY SPECIFICATION
==============================================================================
Role: Memory Subsystem Specification
System Context: This document defines the "Memory as Evidence, Not Truth" paradigm
                used by the Local Agent Kernel. It details the flat-file storage
                schema, confidence scoring, and TTL/expiry validation.
==============================================================================
-->

# Memory Subsystem Specification: Evidence-Based Verification

The Local Agent Kernel implements a flat-file memory subsystem designed to minimize redundant execution, reduce LLM API costs, and guarantee high-speed local responses.

## 🧠 Memory as Evidence, Not Truth

In traditional caching, a key-value hit is returned blindly. The Local Agent Kernel treats memory as *evidence* that must clear a strict verification bar before being trusted:

1. **Confidence Threshold:** The stored confidence score must be `>= 90`. If a previous run resulted in low confidence, the kernel will bypass memory and re-execute the module.
2. **Temporal Validity (TTL):** For volatile modules, the kernel checks the `expiry` timestamp. If the current time exceeds the expiry, the entry is treated as stale and re-executed.
3. **Dependency Integrity:** If a module depends on external files or other modules, the kernel verifies that those dependencies have not changed since the last execution.

## 📁 Flat-File JSON Schema

Memory is persisted in a single, flat JSON file at `memory/local/memory.json`. This ensures zero external database dependencies and allows the kernel to run seamlessly in Termux or Colab.

### Schema Definition

```json
{
  "module_name": {
    "result": "The actual output string captured from stdout",
    "confidence": 99,
    "last_verified": "YYYY-MM-DD HH:MM:SS",
    "dependencies": []
  }
}
```

### Example Entry

```json
{
  "sky_colour": {
    "result": "The sky is blue during clear daylight.",
    "confidence": 99,
    "last_verified": "2026-07-29 05:13:02",
    "dependencies": []
  }
}
```

## ⚡ Performance Impact

- **Memory Hit:** ~1-5ms (Close to instant, zero network overhead, zero API costs).
- **Memory Miss:** ~500ms - 3000ms (Requires LLM routing and subprocess execution).