# Tessera — Architecture

> This document explains *why* Tessera is built the way it is. For *how* to use it, see [docs/getting-started.md](docs/getting-started.md). For measured performance numbers, see [BENCHMARK.md](BENCHMARK.md).

---

## The core thesis

Most AI agent frameworks treat the LLM as the only tool. Every query — even repeated ones — pays for a fresh LLM call. Every computation — even `2 + 2` — is guessed by a language model.

Tessera flips this: **the LLM is a router, not the executor.** The actual work happens in deterministic modules that can be cached, audited, and trusted.

This is not a chatbot framework. It is an **operating system for agent capabilities**, where:

- The **kernel** routes requests, manages memory, and orchestrates execution
- The **modules** do the actual work — and they can be anything that speaks JSON
- The **cache** makes repeated work free, across both literal and semantic equivalence

## System Integrity & Diagnostics

Tessera utilizes a dedicated **Diagnostic Engine** (siphoned from enterprise-grade agent kernels) to ensure system health. Before any kernel execution cycle, the system performs a deep-check of:

1. **Environment Integrity:** Validates API keys, path configurations, and runtime dependencies.
2. **Memory Persistence:** Ensures the `memory/` layer is writable and consistent.
3. **Module Registry:** Verifies that all registered modules are executable and compliant with the Zero-Leak Sandbox architecture.

*Failure to pass these checks results in a fail-fast state to prevent cache poisoning or undefined behavior.*

## Component overview

```
                    ┌─────────────────────────────────────────┐
                    │              Tessera Kernel             │
                    │                                         │
   user request ───►│  1. Cache lookup (intent-clustered)    │
                    │     ├─ hit  ──► return cached result    │
                    │     └─ miss ──► continue                │
                    │                                         │
                    │  2. Router cache lookup                 │
                    │     ├─ hit  ──► skip LLM, use cached    │
                    │     │           module decision         │
                    │     └─ miss ──► continue                │
                    │                                         │
                    │  3. LLM Router (Gemini/OpenAI/local)    │
                    │     └─ fallback ─► keyword routing      │
                    │                                         │
                    │  4. Module execution (subprocess)       │
                    │     └─ stdout captured → cached → return│
                    │                                         │
                    └─────────────────────────────────────────┘
                                          │
                                          ▼
                              ┌──────────────────────┐
                              │   Module Registry    │
                              │                      │
                              │  general_qa    (LLM) │
                              │  pixel_analyzer(numpy)│
                              │  calculator    (math)│
                              │  ...your modules...  │
                              └──────────────────────┘
```

## Security & Compliance

To maintain enterprise-grade stability, Tessera enforces:

- **Zero-Leak Sandbox:** Modules are isolated via subprocesses. Memory management is strictly enforced using `WeakMap` patterns in the kernel to prevent long-running process leaks.
- **Diagnostic Telemetry:** Every execution cycle generates a diagnostic manifest, ensuring auditability of routing decisions and module performance.
- **Consensus Weighting:** Enterprise modules utilize dynamic consensus weighting to validate outputs across multiple providers before committing to the cache.

## Decoupled components

Every component is an interface, not a concrete class. This is the open-core boundary.

| Component | Interface | Default impl | Enterprise impl |
|-----------|-----------|--------------|-----------------|
| `Cache` | `get(key) / set(key, val, ttl)` | `FileCache` (JSON on disk) | `RedisCache` (distributed) |
| `Router` | `route(request, registry) → module_name` | `LLMRouter` (Gemini/OpenAI/DeepSeek/local) | Custom (e.g. fine-tuned classifier) |
| `RouterCache` | `get_decision(request) / set_decision(request, module)` | `FileCache` (separate namespace) | `RedisCache` |
| `ModuleRegistry` | `discover() / get(name) / cluster_key(name, request)` | `FileSystemRegistry` (scans `modules/`) | `RemoteRegistry` (HTTP-discovered) |

## The three cache-key strategies

### 1. `static` — one slot per module
### 2. `request` — one slot per unique phrasing
### 3. `extract:<pattern>` — semantic clustering

## The router cache

Cache the routing decision itself: `(request_hash → module_name)`. This pushes break-even from ~50% hit rate down to ~20%.

## Module contract

A Tessera module is **any executable** that:

1. Lives at `modules/<name>/`
2. Has a `README.md` declaring `name:`, `purpose:`, and optionally `cluster_key:`
3. Has a `run.sh` (or any executable) that reads `AI_AGENT_REQUEST` and writes to stdout.

## Failure modes

- **Diagnostic check fails:** Kernel refuses to start (fail-fast).
- **Module crashes:** Error message returned, **not cached** (prevents poison).

## Open-core boundary

The boundary is **scalability and governance**. Enterprise features include RBAC, token budget management, compliance audit logging, and container-based sandboxing.