# What this actually does

A plain walkthrough of the mechanism, no setup steps. If README.md is
"how to run it," this is "what happens when you do."

## The short version

You type a request. The kernel decides which module answers it, checks
if it's already answered that exact thing before, and either reuses the
old answer or runs the module fresh. Either way you get a result.

## Step by step, in order

1. **You run:** `python3 kernel.py "what colour is the sky"`

2. **Kernel loads `.env`** (if one exists) so any API keys you've set are
   available. If there's no `.env` file, nothing breaks — it just has no
   keys to try.

3. **Kernel builds a list of available modules** by scanning every
   `modules/*/README.md` and pulling out the `name` and `purpose` fields.
   This list is rebuilt fresh every run — if you added a module five
   minutes ago, it's already in the list. Nothing to register by hand.

4. **Kernel decides which module handles the request.** It tries, in
   order: Gemini, OpenAI, DeepSeek, a local model, then plain keyword
   matching. It stops at the first one that gives it a usable answer.
   Whichever one it used gets printed in the output, so you always know
   whether an LLM was actually involved or it fell back to keywords.

5. **Kernel checks memory for that module.** `memory/local/memory.json`
   holds every result the kernel has produced before, one entry per
   module, along with a confidence score and a timestamp. If there's a
   matching entry and its confidence is high enough, the kernel stops
   here and hands back the stored result. **No module runs, no LLM gets
   called a second time.** This is the entire point of having memory —
   the same question doesn't get re-solved from scratch every time.

6. **If there was no usable memory entry, the module actually runs.**
   The kernel finds the module's `run.sh`, executes it, and captures
   whatever it prints.

7. **The result gets written to memory** — the output, a confidence
   score, and the time it was produced — so the next time this module
   is needed, step 5 can short-circuit straight to the answer.

8. **You get the result printed back**, along with which route it took
   (which LLM, or keyword fallback) and whether it came from memory or
   from actually running something.

## What "memory" means here, concretely

It's one JSON file. Each module gets one entry:

\`\`\`json
{
  "sky_colour": {
    "result": "The sky is blue during clear daylight.",
    "confidence": 99,
    "last_verified": "2026-07-29 05:13:02",
    "dependencies": []
  }
}
\`\`\`

Nothing fancier than that. No database, no external service. The kernel
reads this file, decides if an entry is trustworthy enough to reuse, and
writes back to it after running something new.

## What a "module" actually is

A folder with two files:

- `README.md` — a small YAML block describing what the module does,
  what it needs as input, what it produces, and whether it's
  experimental, testing, stable, or deprecated.
- `run.sh` — the actual script. Whatever it prints to stdout becomes
  the module's result.

The kernel doesn't know or care what's inside `run.sh`. It just runs it
and reads what comes out. That's what lets any number of unrelated
modules coexist without the kernel needing special-case code for each
one.

## What the LLM is actually used for right now

Just one thing: picking which module should handle a request, out of
the list the kernel built in step 3. It is not writing code, not
executing anything, not touched by memory. If it says a module that
doesn't exist, the kernel ignores that answer and falls through to the
next provider, then eventually to keyword matching.

## What proves this is working

Run the same request twice in a row.

- **First run** — you'll see `memory miss — executed <module>`, and it
  takes measurably longer, because it actually ran the module (and
  possibly called an LLM to route it).
- **Second run** — you'll see `memory hit — no module execution`, and
  it returns close to instantly, because nothing ran except a file read.

That difference — same answer, far less work the second time — is the
whole mechanism working as intended.
