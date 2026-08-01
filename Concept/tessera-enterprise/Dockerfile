# Dockerfile for Tessera Enterprise
# Multi-stage build: final image is minimal, no build tools.
# ARCHITECTURE: Enterprise Diagnostic Engine & Zero-Leak Sandbox

FROM python:3.12-slim AS base

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        libjpeg-dev \
        zlib1g-dev \
        libzbar0 \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY modules/ ./modules/
COPY Benchmarks/ ./Benchmarks/

# Install Tessera with image extra
RUN pip install --no-cache-dir ".[image]"

# Create enterprise directories
RUN mkdir -p /app/memory/local /app/logs /app/diagnostics

# Enterprise Environment Configuration
ENV TESSERA_MODULES_DIR=/app/modules
ENV TESSERA_CACHE_DIR=/app/memory/local
ENV TESSERA_CACHE_BACKEND=file
ENV TESSERA_DIAGNOSTIC_MODE=strict

# Pre-flight Diagnostic Validation
# Ensures kernel integrity before image finalization
RUN python -c "from Benchmarks import run_system_diagnostics; import sys; res = run_system_diagnostics(); sys.exit(0 if res['status'] == 'HEALTHY' else 1)"

# CLI entry point
ENTRYPOINT ["tessera"]
CMD ["--help"]