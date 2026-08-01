# Dockerfile for Tessera Enterprise
# Role: Multi-stage build for high-integrity enterprise deployment.
# Architecture: Diagnostic Engine & Zero-Leak Sandbox integration.

FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libjpeg-dev \
        zlib1g-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY modules/ ./modules/
COPY Benchmarks/ ./Benchmarks/

# Install dependencies and build
RUN pip install --no-cache-dir ".[image]"

# Pre-flight Diagnostic Validation
# Ensures kernel integrity before image finalization
RUN python -c "from Benchmarks import run_system_diagnostics; import sys; res = run_system_diagnostics(); sys.exit(0 if res['status'] == 'HEALTHY' else 1)"

FROM python:3.12-slim AS final

# Create non-root user for Zero-Leak security
RUN groupadd -r tessera && useradd -r -g tessera -s /bin/false tessera

WORKDIR /app

# Copy only necessary artifacts from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /build/src ./src
COPY --from=builder /build/modules ./modules

# Create enterprise directories with correct ownership
RUN mkdir -p /app/memory/local /app/logs /app/diagnostics && \
    chown -R tessera:tessera /app

# Enterprise Environment Configuration
ENV TESSERA_MODULES_DIR=/app/modules
ENV TESSERA_CACHE_DIR=/app/memory/local
ENV TESSERA_CACHE_BACKEND=file
ENV TESSERA_DIAGNOSTIC_MODE=strict

USER tessera

# CLI entry point
ENTRYPOINT ["tessera"]
CMD ["--help"]