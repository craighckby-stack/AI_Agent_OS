# Writing Tessera Modules

<!-- 
  ARCHITECTURAL HEADER: Tessera Module Development Guide
  Role: Defines the contract for module creation, diagnostic integration, and caching strategies.
  Integration: Linked to the Diagnostic Engine for pre-flight validation and kernel execution cycles.
-->

A Tessera module is **any executable** that follows a simple contract. You
can write one in 30 seconds.

## The contract

A module is a directory under `modules/` containing:

1. **`README.md`** — declares the module's metadata
2. **`run.sh`** — an executable that does the work

That's it. No base class to inherit. No framework to import. No Python
required — any language works.

## Minimal example

```bash
mkdir -p modules/hello
cat > modules/hello/README.md <<EOF
name: hello
purpose: Greets the user
cluster_key: static
EOF

cat > modules/hello/run.sh <<EOF
#!/bin/bash
echo "Hello, world!"
EOF

chmod +x modules/hello/run.sh

tessera "say hello"
# Result: Hello, world!
```

## The README.md fields

```yaml
name: my_module          # Required. The unique module identifier.
purpose: <one line>      # Required. Used by the LLM router to pick this module.
cluster_key: <strategy>  # Optional. Defaults to 'request'. See below.
```

## Diagnostic Integrity (Enterprise Requirement)

Modules integrated into the Enterprise environment are subject to the **Enterprise Diagnostic Engine** pre-flight checks. Ensure your module:
- Does not block execution during the `diagnostic-check` phase.
- Returns a non-zero exit code if critical dependencies (e.g., local data files, API keys) are missing.
- Logs diagnostic telemetry to `stderr` to avoid polluting the kernel cache.
- Adheres to the `Zero-Leak` security standard by ensuring no sensitive data is written to logs or temporary files.

## Cluster key strategies

This is the most important decision when writing a module. It controls
how the kernel caches your module's output.

### `static` — one slot per module

Use when your module **always returns the same answer** regardless of input.

```yaml
cluster_key: static
```

Examples: hardcoded facts, configuration lookups, anything deterministic
where the output never varies.

Cache key: `module_name` (literally just the name).

### `request` — one slot per unique phrasing

Use when your module's output **depends on the exact request** (typically
LLM-backed modules).

```yaml
cluster_key: request
```

Examples: general Q&A, summarization, anything where the same phrasing
should return the same answer but different phrasings might differ.

Cache key: `module_name::md5(request)[:10]`

### `extract:image` — semantic cluster by image

Use when your module processes **an image** and the same image always
produces the same output regardless of how the user phrases the request.

```yaml
cluster_key: extract:image
```

The kernel extracts any image filename from the request (`.jpg`, `.png`,
etc.) and uses just the filename as the cluster token. All phrasings about
the same image share one cache slot.

Cache key: `module_name::cluster::<filename>`

### `extract:url` — semantic cluster by URL

Use when your module processes **a URL** and the same URL always produces
the same output.

```yaml
cluster_key: extract:url
```

Cache key: `module_name::cluster::<url>`

## Reading the request

Your `run.sh` receives the user's request in the `AI_AGENT_REQUEST`
environment variable:

```bash
#!/bin/bash
REQUEST="$AI_AGENT_REQUEST"
echo "You asked: $REQUEST"
```

## Writing output

Write your result to **stdout**. The kernel captures it, caches it, and
returns it to the user.

```bash
#!/bin/bash
echo "Here is the result of my computation"
```

## Exit codes

- **Exit 0** → success, stdout is cached and returned
- **Exit non-zero** → failure, stderr is logged, **nothing is cached**

The "never cache failures" rule is critical: a transient network error
shouldn't poison the cache for future requests.

## Caching inside your module (optional)

Your module can maintain its own cache in addition to the kernel's cache.
This is useful for expensive sub-operations.

```bash
#!/bin/bash
MODULE_DIR="$(cd "$(dirname "$0")" && pwd)"
CACHE_DIR="$MODULE_DIR/.cache"
mkdir -p "$CACHE_DIR"

# Hash the request
CACHE_KEY=$(echo -n "$AI_AGENT_REQUEST" | md5sum | cut -d' ' -f1)
CACHE_FILE="$CACHE_DIR/${CACHE_KEY}.json"

# Cache hit?
if [ -f "$CACHE_FILE" ]; then
    cat "$CACHE_FILE"
    exit 0
fi

# Cache miss — do the work
RESULT=$(expensive_operation)

# Cache and return
echo -n "$RESULT" > "$CACHE_FILE"
echo "$RESULT"
```

## A real example: image analysis module

See `modules/pixel_analyzer/` for a complete example that:
- Uses `cluster_key: extract:image` for semantic caching
- Has its own per-image disk cache (by file hash)
- Does real computation with PIL + numpy
- Returns structured JSON output

## Module discovery

The kernel scans `modules/*/README.md` on startup. To add a module:
1. Create a directory under `modules/`
2. Add `README.md` with the required fields
3. Add `run.sh` (or any executable named `run.sh`)
4. Make `run.sh` executable: `chmod +x run.sh`

No restart needed — the kernel re-scans on each request.

## Testing your module

```bash
# Test directly (bypass the kernel)
AI_AGENT_REQUEST="test request" bash modules/my_module/run.sh

# Test through the kernel
tessera "use my module for this test request"
```

## Best practices

1. **Be deterministic.** Same input → same output. This is what makes
   caching trustworthy.
2. **Fail loudly.** Exit non-zero on failure. Don't return partial or
   garbage output — the kernel won't cache it.
3. **Keep stdout clean.** Only the result goes to stdout. Diagnostic
   output goes to stderr.
4. **Use the cluster key wisely.** `static` for true constants,
   `extract:*` for object-keyed work, `request` for everything else.
5. **Don't call the LLM unless you have to.** If your module can do
   the work deterministically, do it. The LLM is for routing, not
   execution.