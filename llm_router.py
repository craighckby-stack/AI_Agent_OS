"""
LLM routing chain — stand-in for the "LLM Interface Layer" in
AI_Agent_OS_Architecture.md Section 4.

Tries providers in order until one answers. Each provider is skipped
(not failed) if its API key isn't set, so partial setups still work.
If every provider is unavailable, the caller should fall back to the
keyword routing table in kernel.py — the LLM layer is an upgrade, not
a hard requirement.

NOT YET RUN AGAINST A LIVE KEY — the sandbox this was written in can't
reach these APIs. Verify against a real key before relying on it.

Order: Gemini -> OpenAI -> DeepSeek -> local model (Ollama).
"""

import json
import os
import urllib.request
import urllib.error

TIMEOUT = 10  # seconds — fail fast, don't hang the kernel on a dead API


def _build_prompt(request: str, registry: dict) -> str:
    modules_desc = "\n".join(
        f"- {name}: {meta['purpose']}" for name, meta in registry.items()
    )
    return (
        "You are the routing layer of a local agent kernel. Given a user "
        "request, choose exactly one module from the list below that should "
        "handle it. Respond with ONLY a JSON object of the form "
        '{"module": "<name>"} and nothing else. If nothing fits, respond '
        '{"module": null}.\n\n'
        f"Available modules:\n{modules_desc}\n\n"
        f"Request: {request}"
    )


def _extract_module(text: str) -> str | None:
    try:
        # Models sometimes wrap JSON in ```json fences despite instructions
        cleaned = text.strip().strip("`").replace("json\n", "", 1).strip()
        data = json.loads(cleaned)
        return data.get("module")
    except (json.JSONDecodeError, AttributeError):
        return None


def _post_json(url: str, headers: dict, payload: dict) -> dict | None:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def _try_gemini(prompt: str) -> str | None:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={key}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    data = _post_json(url, {"Content-Type": "application/json"}, payload)
    if not data:
        return None
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return None


def _try_openai(prompt: str) -> str | None:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
    }
    data = _post_json(url, headers, payload)
    if not data:
        return None
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return None


def _try_deepseek(prompt: str) -> str | None:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        return None
    # DeepSeek's API is OpenAI-compatible
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
    }
    data = _post_json(url, headers, payload)
    if not data:
        return None
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return None


def _try_local(prompt: str) -> str | None:
    # Local model via Ollama (or anything speaking the same API), e.g. on
    # the S23 through Termux running `ollama serve`. Set LOCAL_LLM_URL to
    # override the default.
    url = os.environ.get("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
    model = os.environ.get("LOCAL_LLM_MODEL", "llama3.2")
    payload = {"model": model, "prompt": prompt, "stream": False}
    data = _post_json(url, {"Content-Type": "application/json"}, payload)
    if not data:
        return None
    return data.get("response")


PROVIDERS = [
    ("gemini", _try_gemini),
    ("openai", _try_openai),
    ("deepseek", _try_deepseek),
    ("local", _try_local),
]


def route_via_llm(request: str, registry: dict) -> tuple[str | None, str | None]:
    """
    Returns (module_name, provider_used). Both are None if every provider
    was unavailable or failed — caller should fall back to keyword routing.
    """
    prompt = _build_prompt(request, registry)
    for name, fn in PROVIDERS:
        raw = fn(prompt)
        if raw is None:
            continue  # not configured, or the call failed — try next
        module = _extract_module(raw)
        if module:
            return module, name
    return None, None
