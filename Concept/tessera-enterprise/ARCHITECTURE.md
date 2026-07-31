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

### Decoupled components

Every component is an interface, not a concrete class. This is the open-core boundary.

| Component | Interface | Default impl | Enterprise impl |
|-----------|-----------|--------------|-----------------|
| `Cache` | `get(key) / set(key, val, ttl)` | `FileCache` (JSON on disk) | `RedisCache` (distributed) |
| `Router` | `route(request, registry) → module_name` | `LLMRouter` (Gemini/OpenAI/DeepSeek/local) | Custom (e.g. fine-tuned classifier) |
| `RouterCache` | `get_decision(request) / set_decision(request, module)` | `FileCache` (separate namespace) | `RedisCache` |
| `ModuleRegistry` | `discover() / get(name) / cluster_key(name, request)` | `FileSystemRegistry` (scans `modules/`) | `RemoteRegistry` (HTTP-discovered) |

A developer can swap any component in two lines:

```python
from tessera import Kernel, RedisCache

kernel = Kernel(cache=RedisCache(url="redis://..."))
kernel.run("what colour is the sky")
```

## The three cache-key strategies

This is the most important architectural decision in Tessera. Different modules need different caching strategies.

### 1. `static` — one slot per module

For modules that always return the same answer regardless of phrasing.

```yaml
# modules/sky_colour/README.md
name: sky_colour
purpose: Returns the colour of the sky
cluster_key: static
```

Cache key: `sky_colour`

**Use case:** Hardcoded facts, configuration lookups, anything deterministic-by-design.

### 2. `request` — one slot per unique phrasing

For modules whose output depends on the exact request (typically LLM-backed modules).

```yaml
# modules/general_qa/README.md
name: general_qa
purpose: LLM-backed fallback for arbitrary questions
cluster_key: request
```

Cache key: `general_qa::md5(request)[:10]`

**Use case:** LLM-backed Q&A where the same phrasing should return the same answer, but different phrasings might get different answers.

### 3. `extract:<pattern>` — semantic clustering

For modules whose output depends on an **object** referenced in the request, not the phrasing.

```yaml
# modules/pixel_analyzer/README.md
name: pixel_analyzer
purpose: Analyzes image color composition
cluster_key: extract:image
```

Cache key: `pixel_analyzer::cluster::sample.jpg`

**Use case:** Image analysis (same image → same analysis regardless of phrasing), document processing (same doc → same summary), database lookups (same query → same result).

This is the strategy that delivers **98.7% cost savings** — see [BENCHMARK.md](BENCHMARK.md).

## The router cache

The router cache is the feature that drops the break-even cache-hit rate from ~50% to ~20%.

### The problem

Even with cache-before-router, every cache *miss* pays the full LLM router call (~128 tokens) just to decide which module to invoke. If a user asks 10 semantically-equivalent questions about the same image, the router is called 10 times — once per miss — even though it would make the same decision each time.

### The solution

Cache the routing decision itself: `(request_hash → module_name)`. On a cache miss in the result cache, check the router cache. If the router has seen this exact request before, skip the LLM call and use the cached decision.

```
1. Result cache hit?     → return cached result  (0 LLM calls)
2. Router cache hit?     → execute cached module  (0 LLM calls)
3. LLM router call       → cache decision, execute module  (1 LLM call)
```

### Why this matters

In a typical workload where users phrase the same intent many different ways:
- Without router cache: each unique phrasing pays 128 tokens of router overhead
- With router cache: each unique phrasing pays 0 tokens after the first encounter

This pushes break-even from ~50% hit rate down to ~20% — making Tessera profitable for almost any production workload.

## Module contract

A Tessera module is **any executable** that:

1. Lives at `modules/<name>/`
2. Has a `README.md` declaring `name:`, `purpose:`, and optionally `cluster_key:`
3. Has a `run.sh` (or any executable) that:
   - Reads `AI_AGENT_REQUEST` env var
   - Writes its result to stdout
   - Exits 0 on success, non-zero on failure

### Why subprocess, not Python imports?

Three reasons:

1. **Language agnostic.** A Rust module, a SQL script, a Node.js tool — all valid. The open-core pitch depends on this. If modules had to be Python imports, we'd lock out 70% of the developer ecosystem.

2. **Sandboxing.** Subprocess isolation is the only meaningful security boundary in the absence of a real sandbox. A module that crashes, leaks memory, or hangs cannot corrupt the kernel. (Future enterprise feature: proper container sandboxing with seccomp/firejail.)

3. **Determinism.** A subprocess that reads `AI_AGENT_REQUEST` and writes to stdout has no hidden state. Same input → same output. This is what makes caching trustworthy.

### The trade-off

Subprocess startup costs ~5-10ms on Linux. For modules that do real work (image analysis: 2-3s, LLM calls: 1-5s), this is invisible. For modules that are pure computation (calculator: <1ms), the overhead is significant.

**Mitigation:** The `static` and `extract:*` cache strategies mean the subprocess only runs once per unique input. After that, the cache serves the result.

## Memory as evidence, not truth

Cached entries include:
- `result`: the module's stdout
- `confidence`: 0-100 (default 99 for successful execution)
- `last_verified`: timestamp
- `dependencies`: list of upstream resources the result depends on (future)

The kernel treats memory as **evidence**, not truth. On lookup, it checks:
- Is `confidence` ≥ threshold (default 90)?
- Has the entry expired? (future: TTL per cluster)
- Have any dependencies changed? (future: dependency invalidation)

If any check fails, the kernel re-executes the module and updates the entry.

## Failure modes

Tessera is designed to **degrade gracefully**:

| Failure | Behavior |
|---------|----------|
| No LLM API keys configured | Keyword-only routing (router cache + ROUTING_TABLE) |
| All LLM providers fail | Keyword fallback, then default module |
| Module crashes (non-zero exit) | Error message returned, **not cached** (prevents poison) |
| Module times out | Error message returned, not cached |
| Cache file corrupted | Treated as cache miss, kernel continues |
| Diagnostic check fails | Kernel refuses to start (fail-fast) |

The principle: **a transient failure should never poison the cache.** Failed executions are not cached. The next request for the same query will re-execute the module and may succeed.

## Open-core boundary

What's free (Apache 2.0):
- The kernel
- The router (multi-provider LLM with fallback)
- The router cache
- The cache interface + `FileCache` implementation
- The module registry
- All reference modules

What's enterprise (`tessera-enterprise`, separate package):
- `RedisCache` / `MemcachedCache` (distributed caching)
- RBAC per module
- Token budget management
- Compliance audit logging
- Module sandboxing (container-based)
- Remote module registry (HTTP-discovered modules)

The boundary is **scalability and governance**, not features. A single developer can run Tessera locally with all features. An enterprise pays for the ability to run it across a fleet with audit trails.
