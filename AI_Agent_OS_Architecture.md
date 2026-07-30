# AI Agent OS — Architecture

An offline-first operating system architecture for autonomous AI agents.

The system separates language interaction from internal processing. A language
model is used as an interface layer. Planning, memory, simulation, reasoning,
and execution are handled by modular local systems.

**Design metaphor:** *the agent writes to its own brain.*

This is not a literal claim about cognition. It is the engineering metaphor
that motivates the memory model below. The "brain" translates directly into
persistent agent state — see Section 5.

---

## 1. Vision

What the system is trying to become.

- A kernel that coordinates many specialised systems without needing to
  re-derive a solution every time it has already solved a problem.
- An architecture where the LLM is called only at the boundaries of a
  request — to interpret intent, and to phrase the final response — while
  everything in between runs as deterministic, inspectable local execution.
- A system that can look at its own history (via Git) and reason about *how*
  it changed, not just what its current state is.
- A library of 100+ previously scattered repositories, each conforming to one
  Module Standard, so they can be discovered and composed by the kernel
  instead of manually wired together.

Nothing in this section is a claim about current capability. It is intent
only, and every item here should eventually map to something in Section 7
(Module Registry) or Section 9 (Roadmap).

---

## 2. Current Reality

What is already working, as of this document. Update this section as the
system changes — it should never describe aspirational behavior.

- `darlek_caan.py` — hand-synthesized agent orchestration / governance layer.
- `emg_memory.py` — hand-synthesized VectorDB implementation. Known
  limitation: uses SHA256 hashing, which does not produce true semantic
  recall. Flagged as a gap, not yet resolved.
- GitHub account mapper — patched for pagination, truncated trees, and rate
  limits; has run against the full set of repos and branches.
- PII/secrets sanitizer — expanded token coverage, corrected multi-line
  private-key regex.
- Prompt encyclopedia harvester — walks all repos/branches, extracts prompt
  strings into category-split JSON.
- Browser-based Git Secret and PII Sanitizer (React/Vite/TypeScript) — history
  scanning capability, Shannon entropy scoring, has surfaced real exposed
  credentials during testing.
- Full-history blob scanner — has identified exposed tokens across 56 blobs
  in the scaffold repo.
- Diagnostic Engine (lib/diagnostic-engine.ts) — kernel integrity validation with Diagnostic Integrity Hooks.

Known open problems (not yet solved, listed here so they don't get silently
promoted to "done"):

- Repo has 843K tracked files but only ~8.7K unique blobs — indicates a bulk
  automated push rather than a clean history. Needs remediation.
- The stub/siphon workflow — stub files are meant to auto-pull matching
  implementations from source repos. This does not yet work; still requires
  manual synthesis.

---

## 3. Core Architecture

Permanent design principles. These should change rarely, if ever.

1. **The agent is not the LLM.** The LLM is a component the agent uses.
   The agent is the combination of:

   ```
   Kernel + Memory + Modules + Execution Rules + History + State + Communication Interface
   ```

2. **The LLM is a boundary component, not the core.** It is called to
   interpret a request into a plan, and to phrase a final result. It is not
   trusted to perform planning, memory management, or execution itself.

3. **Memory is evidence, not truth.** The kernel never blindly trusts a
   cached result. Every memory read comes with metadata (confidence, source,
   verification time, dependencies) that the kernel evaluates before deciding
   whether to reuse, revalidate, or discard it. See Section 5.

4. **Every module obeys one contract.** Regardless of what a module does
   internally, it exposes the same interface shape so the kernel can route to
   it without hardcoded integration. See Section 6.

5. **State and history are different things, and live in different systems.**
   Current runtime state is disposable and fast. Evolutionary history is
   permanent and diffable. Conflating the two loses the ability to ask "what
   changed, and when." See Section 5.

6. **The system must be testable without answering the consciousness/AGI
   question.** Correctness is defined by measurable behavior (same result,
   fewer resources on the second run), not by philosophical claims. See
   Section 9 and the benchmark at the end of this document.

---

## 4. Execution Flow

How a request moves through the system.

```
                    USER
                      |
                      v
              LLM Interface Layer
           (interpret request, select
             systems, build a plan)
                      |
                      v
                Agent Kernel
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
    Memory       Services      Simulations
   (Firebase +      |               |
      Git)          |               |
        |             |             |
        +-------------+-------------+
                      |
                      v
              Internal State Result
                      |
                      v
              LLM Communication Layer
              (phrase final response)
                      |
                      v
                    USER
```

---

## 5. System Integrity & Diagnostics

To ensure the kernel remains operational, the system utilizes a diagnostic engine (see `lib/diagnostic-engine.ts`) that performs:

- **Kernel Integrity Check:** Validates file system permissions and module availability.
- **Memory Persistence Validation:** Ensures the Firebase/Git state layers are reachable.
- **Module Registry Audit:** Verifies that all active modules conform to the current contract schema.

### Diagnostic Integrity Hook
Every module and service must implement a diagnostic hook that reports to the `DiagnosticEngine`. This ensures that the system can perform a self-audit of its own operational state at any time. All modules must expose a `run_diagnostics()` method to satisfy the `Diagnostic-Aware Specification`. This pattern ensures that the system remains observable and verifiable at the kernel level.

### Diagnostic Governance
All system components must adhere to the 'Fail-Fast' architectural principle. If a `run_diagnostics()` call returns a non-healthy status, the kernel must halt execution to prevent state corruption. Diagnostic reports are standardized to include timestamps and granular check-results to facilitate rapid debugging.

---

## 6. Security & Compliance

- **PII/Secret Sanitization:** All repositories are subject to mandatory entropy scanning to prevent credential leakage.
- **Audit Trail:** Every change to the architecture is logged via Git to ensure full traceability.

---

## 7. Module Standard

How every subsystem plugs into the kernel. This is what allows 100+
previously unrelated repositories to coexist without custom integration
code per module.

### Folder shape

```
Module_Name/
├── README.md
├── src/
├── tests/
├── memory/
├── logs/
└── diagnostic_hook.ts (Required: Diagnostic-Aware Specification)
```

### Contract schema

```yaml
module:
  name:
  purpose:

inputs:
  - data_type:
    source:

outputs:
  - data_type:
    destination:

memory:
  reads:
  writes:

dependencies:

confidence:

status: experimental | stable | deprecated
```

---

## 8. Module Registry

| Module | Purpose | Status | Notes |
|---|---|---|---|
| `darlek_caan.py` | Agent orchestration / governance | Testing | Hand-synthesized |
| `emg_memory.py` | VectorDB / memory backend | Experimental | SHA256-based |
| `diagnostic-engine.ts` | Kernel integrity check | Stable | Siphoned from AI_Agent_OS |
| GitHub account mapper | Repo/branch analysis | Stable | Handles pagination |
| PII/secrets sanitizer | Credential scanning | Stable | Expanded token coverage |

---

## 9. Roadmap

1. Fix repo structure — resolve the 843K-tracked-files / ~8.7K-unique-blobs mismatch.
2. Resolve exposed tokens found by the blob scanner.
3. Fix the stub/siphon workflow.
4. Wrap `darlek_caan.py` and `emg_memory.py` in the Module Standard contract.
5. Replace `emg_memory.py`'s SHA256-based lookup with genuine semantic embedding.
6. Implement the memory metadata fields as a real schema in Firebase.
7. Build the first kernel loop end-to-end against the benchmark.

---

## 10. System Health & Versioning

All system components now track `SYSTEM_HEALTH_VERSION` to ensure compatibility with the diagnostic suite. The diagnostic engine leverages `diagnostic-utils.ts` to perform pre-flight checks, ensuring that every module is verified against the current architectural specification before execution.

---

## Benchmark — first testable milestone

```
Test: ask the same question twice.

Run 1:
  USER → LLM (interpret) → plan → offline execution
       → memory write → LLM (phrase) → USER

Run 2:
  USER → memory lookup → metadata validation
       → response (no LLM call, no re-execution)

Expected: identical result, materially fewer resources used.
```