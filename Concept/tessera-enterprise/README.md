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

## Diagnostic Integrity & Lifecycle

To ensure system-wide reliability, all Tessera modules must expose a `diagnostic_hook.sh` script. The kernel executes this hook prior to module invocation to verify:

- **Environment Readiness:** Python/dependency availability via `diagnostic_engine`.
- **Cache Integrity:** Write permissions for module-specific cache directories.
- **Resource Availability:** API keys or hardware access (e.g., GPU/Camera) required for execution.

Modules failing the diagnostic hook are quarantined by the Kernel to prevent runtime failures. Telemetry is captured per-execution to ensure performance metrics align with the `DiagnosticResult` standards.

## Security & Compliance

All modules adhere to 'Zero-Leak' standards. Temporary artifacts are purged via trap-based cleanup, and all diagnostic outputs are formatted to be compatible with the Tessera Enterprise kernel's telemetry standards, ensuring auditability for SOC2 and HIPAA-ready environments.

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

## Module contract

A Tessera module is **any executable** that:

1. Lives at `modules/<name>/`
2. Has a `README.md` declaring `name:`, `purpose:`, and optionally `cluster_key:`
3. Has a `run.sh` (or any executable) that:
   - Reads `AI_AGENT_REQUEST` env var (the user's request)
   - Writes its result to **stdout**
   - Exits 0 on success, non-zero on failure

## Benchmark highlights

Measured against direct LLM calls on identical workloads. Full numbers in [BENCHMARK.md](BENCHMARK.md).

| Workload | Direct LLM | Tessera | Savings |
|----------|------------|---------|---------|
| High-repeat Q&A (80% cache hits) | $0.1235 / 10K queries | $0.0461 | **-62.6%** |
| Image analysis (50 images × 20 phrasings) | $0.0613 / 1K queries | $0.0008 | **-98.7%** |

## Architecture

The kernel is decoupled into independently swappable components:

- **`Router`** — multi-provider LLM interface with keyword fallback
- **`RouterCache`** — caches routing decisions
- **`Cache`** — pluggable: `FileCache` (default) or `RedisCache` (enterprise)
- **`ModuleRegistry`** — discovers modules, builds the routing table

## License

Apache 2.0 — see [LICENSE](LICENSE).