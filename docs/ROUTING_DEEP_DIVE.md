<!--
==============================================================================
ARCHITECTURAL SYSTEM HEADER: LLM ROUTING & FALLBACK CHAIN DEEP DIVE
==============================================================================
Role: Routing Subsystem Specification
System Context: This document details the multi-provider LLM fallback chain
                and keyword routing table used by the Local Agent Kernel.
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