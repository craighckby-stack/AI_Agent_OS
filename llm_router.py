"""
LLM ROUTER KERNEL | ARCHITECTURAL LAYER 4
Role: Orchestrates intelligent module routing via multi-provider LLM fallback.
Integrates with: kernel.py, diagnostic-engine.py
"""

import json
import os
import urllib.request
import urllib.error
from diagnostic_engine import run_system_diagnostics

TIMEOUT = 10

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
    if not key: return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    data = _post_json(url, {"Content-Type": "application/json"}, payload)
    if not data: return None
    try: return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError): return None

def _try_openai(prompt: str) -> str | None:
    key = os.environ.get("OPENAI_API_KEY")
    if not key: return None
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    data = _post_json(url, headers, payload)
    if not data: return None
    try: return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError): return None

def _try_deepseek(prompt: str) -> str | None:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key: return None
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
    data = _post_json(url, headers, payload)
    if not data: return None
    try: return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError): return None

def _try_local(prompt: str) -> str | None:
    url = os.environ.get("LOCAL_LLM_URL", "http://localhost:11434/api/generate")
    model = os.environ.get("LOCAL_LLM_MODEL", "llama3.2")
    payload = {"model": model, "prompt": prompt, "stream": False}
    data = _post_json(url, {"Content-Type": "application/json"}, payload)
    if not data: return None
    return data.get("response")

PROVIDERS = [("gemini", _try_gemini), ("openai", _try_openai), ("deepseek", _try_deepseek), ("local", _try_local)]

def route_via_llm(request: str, registry: dict) -> tuple[str | None, str | None]:
    # Pre-flight diagnostic check
    diag = run_system_diagnostics()
    if diag.get('status') != 'HEALTHY':
        return None, None
        
    prompt = _build_prompt(request, registry)
    for name, fn in PROVIDERS:
        raw = fn(prompt)
        if raw is None: continue
        module = _extract_module(raw)
        if module:
            return module, name
    return None, None