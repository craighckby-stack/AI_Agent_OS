<!-- 
  FILE: Concept/tessera-enterprise/Docs/getting-started.md
  ROLE: Primary onboarding documentation for the Tessera Enterprise ecosystem.
  INTEGRATION: Connects to the Enterprise Diagnostic Engine and kernel initialization workflows.
-->

# Getting Started with Tessera

## Install

```bash
pip install tessera-os
```

For image analysis module support:

```bash
pip install tessera-os[image]
```

## System Integrity & Pre-flight

Before initializing the kernel, ensure your environment is validated by the Enterprise Diagnostic Engine:

```bash
# Run the diagnostic suite to verify memory, registry, and environment integrity
tessera --diagnostics
```

If the status returns `CRITICAL_FAILURE`, review the diagnostic report generated in the local `/logs` directory before proceeding.

## First run

```bash
# Set at least one LLM provider (or run in keyword-only mode with none)
export GEMINI_API_KEY=your_key_here

# Run a query
tessera "what is the capital of France"
```

## What just happened?

1. Tessera's kernel performed a pre-flight diagnostic check.
2. The kernel received your request.
3. It checked the result cache — miss (first run).
4. It checked the router cache — miss (first run).
5. It called the LLM router to decide which module should handle the request.
6. The router picked `general_qa` (the LLM-backed fallback module).
7. `general_qa` ran, called the LLM, got "Paris", cached the result.
8. The kernel returned the result.

## Run the same query again

```bash
tessera "what is the capital of France"
```

This time:
1. Kernel checked the result cache — **HIT**.
2. Returned the cached answer immediately.
3. **Zero LLM calls. Zero tokens consumed.**

Notice the output says `routed via cache` instead of `routed via llm:gemini`.

## Try a real computation

```bash
tessera "what is 2+2"
```

The router picks `calculator` (a deterministic module). The result is `4`,
computed by Python — not guessed by an LLM. **Zero LLM calls for the
execution itself** (only the router call, which is itself cached on repeat).

## List discovered modules

```bash
tessera --list-modules
```

Output:
```
Discovered 3 modules in ./modules:

  calculator           cluster_key=request        purpose=Evaluates mathematical expressions deterministically...
  general_qa           cluster_key=request        purpose=LLM-backed fallback for arbitrary user questions...
  pixel_analyzer       cluster_key=extract:image  purpose=Performs deep pixel-level color analysis...
```

## Next steps

- [Writing your own module](writing-modules.md)
- [Architecture overview](../ARCHITECTURE.md)
- [Benchmark results](../BENCHMARK.md)
- [Diagnostic Engine Reference](../BENCHMARKS/diagnostic_engine.py)