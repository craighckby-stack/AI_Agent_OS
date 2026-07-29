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

Known open problems (not yet solved, listed here so they don't get silently
promoted to "done"):

- Repo has 843K tracked files but only ~8.7K unique blobs — indicates a bulk
  automated push rather than a clean history. Needs remediation.
- The stub/siphon workflow — stub files are meant to auto-pull matching
  implementations from source repos. This does not yet work; still requires
  manual synthesis.

Anything not listed in this section does not exist yet, regardless of how
often it's referenced elsewhere in this document.

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

The LLM appears exactly twice: entry (interpretation/planning) and exit
(phrasing). Everything between is local, deterministic, and inspectable.

---

## 5. Memory Model

Two systems, two different jobs. Neither substitutes for the other.

### Firebase — runtime state

Fast, volatile, current. Analogous to RAM.

Holds:
- current tasks
- temporary context
- retrieved information
- recent experience / working memory

### Git — evolution history

Persistent, versioned, immutable-by-commit. Analogous to a hard drive, but
more specifically to **version-controlled long-term memory** — not just
storage, but a record of *how* the system changed over time.

Holds:
- system evolution (what changed, when, why)
- successful workflows
- failed experiments
- architecture changes
- knowledge revisions

Because it's Git and not a plain blob store, the agent can `git log` its own
brain: if a workflow that used to work starts failing, the kernel can diff
its own cognitive state and roll back to a prior version rather than
re-deriving a fix from scratch.

### Memory as evidence, not truth

The kernel never returns a cached answer purely because one exists. Every
memory hit is evaluated against its metadata before use.

**Example — stable fact:**

```
Request: "What colour is the sky?"

Memory: Previous answer found.

Metadata:
  workflow used:   sky_colour_v1
  confidence:      99%
  last verified:   recent
  dependencies:    none

Decision: Return cached result. No LLM call required.
```

**Example — volatile fact:**

```
Request: "What is the current weather?"

Memory: Cached answer exists.
        Expiry: exceeded.
        Requires fresh source.

Decision: Kernel wakes the required systems (weather module),
          re-executes, then writes the new result back to memory.
```

The evaluation criteria the kernel checks before trusting a memory hit:

- confidence level
- expiry / TTL
- source reliability
- context match (same question in a different context is not a hit)

### Learning loop

```
New task
  ↓
Search for existing workflow
  ↓
Found + still valid?  →  Reuse, execute, done
  ↓ (no)
Plan via LLM
  ↓
Execute via local systems
  ↓
Evaluate result
  ↓
Store workflow + result + confidence + timestamp
  ↓
Future identical/similar tasks become cheaper
```

---

## 6. Module Standard

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
└── logs/
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

Because every module declares `inputs`, `outputs`, and `dependencies`, the
kernel doesn't need to hardcode how to talk to it — it parses the contract
and routes data accordingly. Because every module declares `status`, the
kernel can apply risk policy: e.g. refuse to route a request that needs 99%
confidence through a module marked `experimental`.

---

## 7. Module Registry

List of all known systems, their maturity, and what they do. This table is
the living inventory — every module recovered from the 106-repo consolidation
lands here once it conforms to Section 6.

| Module | Purpose | Status | Notes |
|---|---|---|---|
| `darlek_caan.py` | Agent orchestration / governance | Testing | Hand-synthesized, not yet contract-wrapped |
| `emg_memory.py` | VectorDB / memory backend | Experimental | SHA256-based; no true semantic recall yet |
| GitHub account mapper | Repo/branch analysis | Stable | Handles pagination, truncated trees, rate limits |
| PII/secrets sanitizer | Credential scanning | Stable | Expanded token coverage, fixed multi-line key regex |
| Prompt encyclopedia harvester | Prompt extraction | Stable | Category-split JSON output |
| Git Secret & PII Sanitizer (React app) | Interactive scanning | Testing | Shannon entropy scoring, history scan |
| Full-history blob scanner | Security audit | Stable | Found 56 blobs with exposed tokens |
| Stub/siphon workflow | Auto-populate stubs from source repos | Experimental | Not working yet — currently manual |

Keep this table honest. A module only moves to `Stable` when it has tests and
has run against real input without manual intervention.

---

## 8. Maturity Levels

- **Experimental** — exists, unproven, may change shape entirely or be
  discarded. Kernel should avoid routing high-confidence requests here.
- **Testing** — working in isolation, not yet integrated against the full
  kernel/memory loop.
- **Stable** — contract-compliant, tested, safe for the kernel to route to
  without supervision.
- **Deprecated** — superseded or retired. Kept for history/rollback
  reference only; kernel should not route to it.

---

## 9. Roadmap

Next integrations, ordered roughly by dependency.

1. Fix repo structure — resolve the 843K-tracked-files / ~8.7K-unique-blobs
   mismatch before building further tooling on top of an inconsistent tree.
2. Resolve exposed tokens found by the blob scanner (56 blobs) — security
   fix, blocks any further public work on the scaffold.
3. Fix the stub/siphon workflow so stub files pull matching implementations
   automatically instead of requiring manual synthesis. This unblocks
   populating the Module Registry from the remaining ~100 source repos.
4. Wrap `darlek_caan.py` and `emg_memory.py` in the Module Standard contract
   (Section 6) so the kernel can route to them instead of calling them ad hoc.
5. Replace `emg_memory.py`'s SHA256-based lookup with genuine semantic
   embedding, since the memory-as-evidence model (Section 5) depends on
   meaningful similarity matching, not hash equality.
6. Implement the memory metadata fields (confidence, TTL, source reliability)
   as a real schema in Firebase, not just a convention.
7. Build the first kernel loop end-to-end against the benchmark below.

---

## Benchmark — first testable milestone

This is deliberately the smallest possible test of the whole architecture.
It sidesteps any question of "is this AGI" and asks only: does the
kernel/memory loop actually behave the way Section 5 says it should.

```
Test: ask the same question twice.

Run 1:
  USER → LLM (interpret) → plan → offline execution
       → memory write → LLM (phrase) → USER

Run 2:
  USER → memory lookup → metadata validation
       → response (no LLM call, no re-execution)

Expected: identical result, materially fewer resources used
          (no LLM call, no module execution) on Run 2.
```

If Run 2 doesn't skip the LLM and doesn't skip execution, the kernel/memory
loop isn't actually working yet — regardless of what any individual module
can do in isolation.
