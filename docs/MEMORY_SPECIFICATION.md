<!--
==============================================================================
ARCHITECTURAL SYSTEM HEADER: EVIDENCE-BASED MEMORY SPECIFICATION
==============================================================================
Role: Memory Subsystem Specification & Governance Controller
System Version: v1.1.0-EVIDENTIAL-INTEGRITY
System Context: This document defines the "Memory as Evidence, Not Truth" paradigm
                used by the Local Agent Kernel. It details the flat-file storage
                schema, confidence decay scoring, TTL validation, dynamic hash auditing,
                and atomic state write operations.
Integrations:
  - kernel.py: Implements the evidence verification logic.
  - modules/: Source of truth for module execution.
  - src/utils/memory_verifier.py: Core evidential memory verification engine.
  - src/utils/memory_decay_engine.py: Mathematical decay computation (Siphoned).
  - src/lib/memory_lifecycle_manager.py: State transition controller.
  - diagnostic_engine.py: System health monitoring and memory persistence probes.
==============================================================================
-->

# Memory Subsystem Specification: Evidence-Based Verification

The Local Agent Kernel implements a zero-dependency, flat-file memory subsystem designed to minimize redundant module execution, eliminate LLM API costs, and guarantee high-speed local response times. 

Unlike traditional Key-Value caches, this system treats memory as **Evidential Assertions**—probabilistic representations of prior state execution that must pass continuous validation gates before being trusted by the kernel.

---

## 🧠 Memory as Evidence, Not Truth

In traditional caching systems, a key-value hit is returned blindly based on key matching. The Local Agent Kernel treats stored memory as *evidence* that must clear a strict verification bar before being accepted as execution context:

1. **Confidence Threshold & Decay:** The stored confidence score must be `>= 90%`. To prevent stale facts from accumulating, memory entries undergo dynamic exponential decay over time based on an configurable half-life model:
   $$
   C(t) = C_0 \times 0.5^{\left(\frac{\Delta t}{\tau}\right)}
   $$
   Where $C_0$ is the initial verification score, $\Delta t$ is elapsed time, and $\tau$ is the entry's half-life parameter. This is programmatically enforced by `src/utils/memory_decay_engine.py`.

2. **Temporal Validity (TTL):** For time-sensitive or volatile modules, the kernel evaluates the `expiry` unix timestamp. If the current epoch time exceeds `expiry`, the entry is flagged as stale, purged, and re-executed.

3. **Cryptographic Dependency Integrity:** If a module depends on external files, environment variables, or sibling modules, the kernel computes and compares SHA-256 digests (`dependency_hash`). If any source dependency changes, the cache entry is invalidated instantly.

4. **Zero-Leak Module Sandboxing:** Scope parameters prevent cross-module memory bleed. Every entry is isolated to its owning module identifier and tenant namespace.

---

## 📁 Tiered Storage Architecture & JSON Schema

To maximize performance while preserving absolute local portability (Termux, Colab, On-Device), memory persistence is organized in a three-tier hierarchy:

- **L1 In-Memory Cache:** Ephemeral dict lookup in kernel memory (~0.05ms).
- **L2 Flat-File JSON Persistence:** Persistent store located at `memory/local/memory.json` (~1-5ms).
- **L3 Verification Archive:** Diagnostic historical log located at `memory/local/archive.json` for telemetry auditing.

### Extended Schema Definition

```json
{
  "module_name": {
    "result": "The actual output string or payload captured from execution",
    "confidence": 99.0,
    "decay_half_life_seconds": 86400,
    "last_verified": "2026-03-30T12:00:00Z",
    "timestamp": 1774872000.0,
    "expiry": 1774958400.0,
    "dependency_hash": "a3f8b910e5218d6c71c1b12d7d8e90ff8a90123456789abcdef0123456789abc",
    "dependencies": ["modules/scanner.py", "config/rules.json"],
    "version": "1.1.0-EVIDENTIAL-INTEGRITY"
  }
}
```

### System Integrity & Atomic Evolution

- **Atomic Write Protocol:** To avoid file corruption during concurrent process execution or ungraceful shutdown, the kernel writes memory updates to a temporary snapshot file (`memory.json.tmp`) and executes an atomic POSIX file rename (`os.replace`).
- **Schema Version Migration:** The `version` metadata field guarantees backward compatibility. Older memory files are updated on-the-fly during boot diagnostic runs.
- **Zero-Leak Isolation:** Module entries are key-namespaced (`tenant_id:module_name`) preventing cross-agent data exposure.

---

## 🔄 Memory State Transition Matrix

Memory entries transition through the following states, managed by `src/lib/memory_lifecycle_manager.py`:

| Current State | Trigger | Next State | Action |
| :--- | :--- | :--- | :--- |
| **EVIDENTIAL** | Decay < 90% | **STALE** | Flag for background refresh |
| **EVIDENTIAL** | Hash Mismatch | **INVALIDATED** | Immediate isolation; purge entry |
| **STALE** | Expiry Reached | **PURGED** | Remove from L2; re-execute module |
| **INVALIDATED** | Re-execution | **EVIDENTIAL** | Update with new hash and 100% confidence |

---

## ⚡ Performance Impact Metrics

| Execution Path | Speed Benchmark | Resource Overhead | Network Cost |
| :--- | :--- | :--- | :--- |
| **L1 Cache Hit** | `~0.05ms` | Near Zero CPU / Minimal RAM | $0.00 |
| **L2 Memory Hit** | `~1 - 5ms` | Local Disk I/O | $0.00 |
| **Memory Miss / Subprocess Execution** | `~500ms - 3000ms` | LLM API Query & Module Run | Standard Token Cost |

---

## 🛡️ Compliance & Verification Engine

All memory operations are governed programmatically by the `MemoryVerifier` utility located at `src/utils/memory_verifier.py`.

```python
from src.utils.memory_verifier import MemoryVerifier

# Initialize Verifier
verifier = MemoryVerifier()

# Verify full memory store integrity
report = verifier.verify_all()
print(f"Store Status: {report['status']}, Valid Entries: {report['valid_entries']}/{report['total_entries']}")
```

- **Automated Audit Routine:** Executed during system bootstrap and kernel idle cycles.
- **Integrity Guarantee:** Entries failing decay, hash, or expiry verification are automatically isolated and marked for re-execution.

---

## 🩺 System Health & Verification (Diagnostic Integrity Hook)

This specification is bound directly to the system's core diagnostic engine (`diagnostic_engine.py`). Any structural deviation in `memory/local/memory.json` triggers a `CRITICAL_FAILURE` diagnostic report.

- **Diagnostic Probe:** The `memory_persistence` health probe executes `verifier.verify_all()` during every deep check.
- **Self-Healing Capability:** If `memory.json` is corrupted or malformed, the memory verifier isolates the malformed entry and initializes a pristine structure without crashing the kernel execution loop.
- **Fail-Fast Mandate:** If an essential module returns an unverified memory state below `90%` confidence, execution bypasses cache and enforces fresh, sandbox-validated execution.

### Memory Integrity Manifest (Programmatic Interface)
```json
{
  "manifest_id": "MEM-SPEC-V1",
  "governance_rules": {
    "min_confidence": 0.90,
    "default_half_life": 86400,
    "enforce_atomic_writes": true,
    "hash_algorithm": "sha256"
  },
  "diagnostic_hooks": [
    "memory_persistence",
    "evidential_decay_check",
    "dependency_integrity_audit"
  ]
}
```