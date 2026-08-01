# Tessera

> An agent OS where modules are tiles. Each module is a discrete capability — a tessera — that composes with others to handle any request. The kernel routes, caches, and orchestrates. Modules do the work.

[![CI](https://github.com/your-org/tessera/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tessera-os.svg)](https://pypi.org/project/tessera-os/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## The 30-second pitch

Most AI agents bleed tokens on every routing decision and hallucinate when asked to do real math or data analysis. **Tessera** intercepts queries via intent-clustered semantic caching and routes them to deterministic, zero-LLM local modules. The result:

- **Up to 98% reduction in LLM API costs** for repetitive workloads
- **100% correctness** on computational tasks (math, image analysis, DB lookups)
- **Language-agnostic modules** — any subprocess that speaks JSON is a Tessera module

## Why it exists

The current generation of AI agent frameworks treat the LLM as the only tool. Every query — even repeated ones — pays for a fresh LLM call. Every computation — even `2 + 2` — is guessed by a language model.

Tessera flips this: the LLM is a **router**, not the executor. The actual work happens in deterministic modules that can be cached, audited, and trusted.

```
user request
    │
    ▼
┌──────────────────────────────────────────────┐
│  Tessera Kernel                              │
│  ┌────────────┐  ┌──────────────────────┐    │
│  │ Memory     │  │ Module Registry      │    │
│  │ (cache)    │  │ (intent clusters)    │    │
│  └────────────┘  └──────────────────────┘    │
│         │                  │                 │
│         ▼                  ▼                 │
│  ┌──────────────────────────────────────┐    │
│  │  Cache hit?  ──── yes ──►  return    │    │
│  │      │                               │    │
│  │      no                              │    │
│  │      ▼                               │    │
│  │  Router Cache hit? ── yes ─► execute │    │
│  │      │                               │    │
│  │      no                              │    │
│  │      ▼                               │    │
│  │  LLM Router (Gemini/OpenAI/local)    │    │
│  │      │                               │    │
│  │      ▼                               │    │
│  │  Execute module ──► cache result     │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

## Quick start

```bash
pip install tessera-os

# Set at least one LLM provider (or run keyword-only mode with none)
export GEMINI_API_KEY=...

# Run a query
tessera "what colour is the sky"
```

### Add your own module

```bash
mkdir modules/my_module
cat > modules/my_module/README.md <<EOF
name: my_module
purpose: Greets the user by name
cluster_key: static
EOF

cat > modules/my_module/run.sh <<EOF
#!/bin/bash
echo "Hello from my_module!"
EOF
chmod +x modules/my_module/run.sh

tessera "use my module"
```

## Diagnostic Integrity

To ensure system-wide reliability, all Tessera modules must expose a `diagnostic_hook.sh` script. The kernel executes this hook prior to module invocation to verify:
- **Environment Readiness:** Python/dependency availability.
- **Cache Integrity:** Write permissions for module-specific cache directories.
- **Resource Availability:** API keys or hardware access (e.g., GPU/Camera) required for execution.

Modules failing the diagnostic hook will be quarantined by the Kernel to prevent runtime failures.

## Module contract

A Tessera module is **any executable** that:

1. Lives at `modules/<name>/`
2. Has a `README.md` declaring `name:`, `purpose:`, and optionally `cluster_key:`
3. Has a `run.sh` (or any executable) that:
   - Reads `AI_AGENT_REQUEST` env var (the user's request)
   - Writes its result to **stdout**
   - Exits 0 on success, non-zero on failure

The kernel handles caching, routing, and memory. Your module just does its job.

### Cluster key strategies

| Strategy | When to use | Cache key |
|----------|-------------|-----------|
| `static` | Module always returns same answer (e.g. `sky_colour`) | `module_name` |
| `request` | Each unique phrasing gets its own slot (e.g. `general_qa`) | `module::md5(request)` |
| `extract:image` | All phrasings about the same image share one slot | `module::cluster::<filename>` |
| `extract:url` | All phrasings about the same URL share one slot | `module::cluster::<url>` |

## Benchmark highlights

Measured against direct LLM calls on identical workloads. Full numbers in [BENCHMARK.md](BENCHMARK.md).

| Workload | Direct LLM | Tessera | Savings |
|----------|------------|---------|---------|
| High-repeat Q&A (80% cache hits) | $0.1235 / 10K queries | $0.0461 | **-62.6%** |
| Image analysis (50 images × 20 phrasings) | $0.0613 / 1K queries | $0.0008 | **-98.7%** |

The image analysis workload also produces **50 structured numeric fields with real pixel data** — the direct LLM produces 0 real data, only hallucinated text.

## Architecture

The kernel is decoupled into independently swappable components:

- **`Router`** — multi-provider LLM interface with keyword fallback
- **`RouterCache`** — caches routing decisions, drops break-even from 50% to 20% hit rate
- **`Cache`** — pluggable: `FileCache` (default, zero-dep) or `RedisCache` (enterprise)
- **`ModuleRegistry`** — discovers modules, builds the routing table, manages intent clusters

A developer can swap any component with two lines of code. See [ARCHITECTURE.md](ARCHITECTURE.md).

## Open core

Tessera is Apache-2.0 licensed. The core kernel, router, cache interface, and module registry are free forever.

**Enterprise features** (separate package, `tessera-enterprise`):
- Distributed Redis/Memcached caching for fleet-wide semantic cache hits
- Role-based access control (RBAC) per module
- Token budget management per user/team
- Compliance audit logging (SOC2, HIPAA-ready)

## Status

- ✅ Core kernel (router, cache, modules)
- ✅ Intent-clustered caching
- ✅ Router cache (routing-decision cache)
- ✅ Reference modules: `general_qa`, `pixel_analyzer`, `calculator`
- 🚧 Redis cache backend
- 🚧 Enterprise audit logging
- 📋 Planned: vector DB cache backend, module sandboxing

## License

Apache 2.0 — see [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) (when it exists) and [docs/writing-modules.md](docs/writing-modules.md). PRs welcome — especially new modules.