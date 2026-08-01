# Deploying Tessera

<!-- 
ARCHITECTURAL ROLE: Deployment documentation for Tessera Enterprise.
INTEGRATION: Connects to the Enterprise Diagnostic Engine and kernel validation pipelines.
-->

## Single-process (development / small scale)

Default configuration. Zero external dependencies.

```bash
pip install tessera-os
export GEMINI_API_KEY=...
tessera "what is the sky color"
```

Cache is stored as JSON files in `./memory/local/`. Suitable for
single-process workloads up to ~1000 queries/day.

## Multi-process (production)

For multi-process or multi-container deployments, use Redis as the
cache backend:

```bash
pip install tessera-os[redis]
export TESSERA_CACHE_BACKEND=redis
export TESSERA_CACHE_REDIS_URL=redis://your-redis-host:6379/0
```

This gives you:
- Shared cache across all worker processes
- Atomic cache writes (no race conditions)
- TTL-based cache expiry
- Cache survives process restarts

## System Integrity & Diagnostic Validation

Before deploying to production, ensure your environment satisfies the Enterprise Diagnostic Engine requirements. The kernel performs a pre-flight check on startup:

```bash
# Manually trigger diagnostic suite to verify environment readiness
python -m tessera.diagnostics.run_check --verbose
```

Ensure the following paths are writable and initialized:
- `/app/memory/`: Persistent state storage
- `/app/modules/`: Dynamic module registry

## Docker

```bash
docker build -t tessera .
docker run -e GEMINI_API_KEY=... tessera "what is 2+2"
```

See `Dockerfile` for the multi-stage build spec, which includes an automated `diagnostic-check` validation step.

## Kubernetes

Recommended deployment:
- **Kernel pods**: stateless, horizontally scalable. Configure with env vars.
- **Redis**: managed Redis instance (ElastiCache, MemoryStore, etc.)
- **Modules**: baked into the kernel image OR mounted as a ConfigMap/Volume

Example deployment manifest (sketch):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tessera
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tessera
  template:
    spec:
      containers:
      - name: tessera
        image: your-registry/tessera:0.1.0
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: tessera-secrets
              key: gemini-api-key
        - name: TESSERA_CACHE_BACKEND
          value: redis
        - name: TESSERA_CACHE_REDIS_URL
          value: redis://redis:6379/0
        - name: TESSERA_MODULES_DIR
          value: /app/modules
```

## Monitoring

Tessera logs to stderr at the `tessera.kernel`, `tessera.router`, and
`tessera.modules` loggers. Configure logging in your application:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

For production, ship logs to your observability stack (Datadog, New
Relic, CloudWatch, etc.).

## Token budget tracking

To track LLM token usage per request, capture the kernel result:

```python
from tessera import Kernel

kernel = Kernel()
result = kernel.run("what is the sky color")
# result.llm_tokens_in and result.llm_tokens_out are populated when
# the LLM router was called (0 on cache hits)
```

For fleet-wide budget tracking, use the enterprise audit log feature
(`tessera-enterprise` package).