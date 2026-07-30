<!--
==============================================================================
ARCHITECTURAL SYSTEM HEADER: LLM ROUTING & FALLBACK CHAIN DEEP DIVE
==============================================================================
Role: Routing Subsystem Specification & Governance Controller
System Context: This document details the multi-provider LLM fallback chain
                and keyword routing table used by the Local Agent Kernel.
                Integrates with: kernel.py, llm_router.py, env_loader.py, RoutingValidator
Diagnostic Integrity Hook: system.routing.integrity_check()
==============================================================================
-->

# Routing Subsystem: Multi-Provider Fallback Chain

The Local Agent Kernel features a resilient routing layer that guarantees request resolution even under severe network degradation or API key exhaustion.

## ⛓️ The Fallback Chain

The routing layer attempts to resolve the target module using the following prioritized chain:

```
[Gemini] ---> [OpenAI] ---> [DeepSeek] ---> [Local (Ollama)] ---> [Keyword Table]
```

1. **Gemini (Google):** Primary high-thinking router.
2. **OpenAI:** Secondary fallback router.
3. **DeepSeek:** Tertiary fallback router.
4. **Local Model (Ollama):** Offline fallback router (e.g., running on-device via Termux).
5. **Keyword Table:** Last-resort deterministic fallback.

## 📝 Prompt Construction

The LLM router dynamically constructs a prompt containing the user request and the up-to-date registry of available modules:

```
You are the routing layer of a local agent kernel. Given a user request, choose exactly one module from the list below that should handle it. Respond with ONLY a JSON object of the form {"module": "<name>"} and nothing else. If nothing fits, respond {"module": null}.

Available modules:
- sky_colour: Answer stable, non-volatile factual questions about sky colour.

Request: what colour is the sky
```

## 🛠️ Robust JSON Extraction

To handle model variance, the router strips markdown code fences (e.g., ` ```json `) and parses the raw JSON string safely:

```python
def _extract_module(text: str) -> str | None:
    try:
        cleaned = text.strip().strip("`").replace("json\n", "", 1).strip()
        data = json.loads(cleaned)
        return data.get("module")
    except (json.JSONDecodeError, AttributeError):
        return None
```

## 🔑 Keyword Fallback Table

If all LLM providers fail or are unconfigured, the kernel falls back to a local, deterministic keyword routing table:

```python
ROUTING_TABLE = {
    "sky": "sky_colour",
    "colour": "sky_colour",
    "color": "sky_colour",
}
```

## 🩺 System Health & Verification

- **Environment Resilience:** The system utilizes a 5-pass iterative variable expansion engine (`expand_variables`) to resolve nested environment dependencies before routing begins.
- **Zero-Leak Sandboxing:** Module execution is isolated via `subprocess.run` with captured output, ensuring that module-level failures do not propagate to the kernel core.
- **Memory-as-Evidence:** Routing results are cached in `memory.json` with a 90% confidence threshold requirement, preventing stale or low-quality data from polluting the execution flow.
- **Diagnostic Integrity:** The routing subsystem is subject to continuous integrity verification. The `RoutingValidator` utility (see `src/lib/routing-validator.ts`) performs runtime checks against the `ROUTING_TABLE` and fallback chain availability to ensure system compliance with the defined architectural manifest.

## 🛡️ Compliance & Verification

All routing operations MUST be validated against the `DiagnosticReport` schema defined in `lib/diagnostic-engine.ts`. Any deviation from the defined fallback chain triggers an automatic kernel re-initialization sequence.

### Programmatic Contract
```typescript
import { runSystemDiagnostics } from './lib/diagnostic-engine';

// Verify routing subsystem health
const report = await runSystemDiagnostics();
if (report.status !== 'HEALTHY') {
  console.error("Routing subsystem integrity breach detected.");
}
```