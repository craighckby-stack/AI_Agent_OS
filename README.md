# agent-os

Local agent kernel — module loader, flat-file memory, LLM routing with
automatic fallback. Runs unchanged in Colab or on-device via Termux.

## Setup

1. Extract this package:

       tar -xzf agent-os.tar.gz
       cd agent-os

2. Copy the env template and add whichever API key(s) you have:

       cp .env.example .env

   Open `.env` and fill in any of: `GEMINI_API_KEY`, `OPENAI_API_KEY`,
   `DEEPSEEK_API_KEY`. None are required — leave them blank and the kernel
   still runs using keyword matching instead of an LLM.

3. Run it:

       python3 kernel.py "what colour is the sky"

4. Run the same command again. First run executes the module and saves
   the result. Second run should return instantly from memory instead of
   running anything — check the output line, it says which happened.

That's it. No install step beyond having Python 3.

## Adding a new module

1. Create a folder under `modules/` — name it whatever the module does.
2. Add two files inside it:
   - `README.md` — the contract (see `modules/sky_colour/README.md` for
     the format: name, purpose, inputs, outputs, dependencies, status).
   - `run.sh` — the script that actually does the work, prints its result
     to stdout.
3. Nothing else to register. The kernel scans `modules/*/README.md`
   automatically, so a new module is usable the moment its folder exists.

## How routing works

When you give it a request, the kernel tries in this order and stops at
the first one that works:

    Gemini -> OpenAI -> DeepSeek -> local model (Ollama) -> keyword match

Whichever key(s) you set in `.env` get tried first. If none are set, or
they all fail, it falls back to plain keyword matching so it still runs.

NOTE: the LLM chain is written but hasn't been tested against a live key
yet. Test it against your own key before relying on it.

## Files

    kernel.py                — runs everything: routes, checks memory, executes, saves
    llm_router.py             — the Gemini/OpenAI/DeepSeek/local fallback chain
    env_loader.py             — reads .env, no extra install needed
    modules/<name>/README.md  — contract for each module
    modules/<name>/run.sh     — the module's actual script
    memory/local/memory.json  — saved results, created automatically on first run

## Firebase

Not used. Everything above runs on flat files only. Can be added later as
an alternate memory backend without changing any module.
