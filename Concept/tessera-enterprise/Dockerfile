# Dockerfile for Tessera
# Multi-stage build: final image is minimal, no build tools.

FROM python:3.12-slim AS base

# Install system deps needed by some modules (PIL needs libjpeg, zbarimg needs libzbar)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libjpeg-dev \
        zlib1g-dev \
        libzbar0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy pyproject and install first (better layer caching)
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY modules/ ./modules/

# Install Tessera with image extra
RUN pip install --no-cache-dir ".[image]"

# Create cache directory
RUN mkdir -p /app/memory/local

# Default config
ENV TESSERA_MODULES_DIR=/app/modules
ENV TESSERA_CACHE_DIR=/app/memory/local
ENV TESSERA_CACHE_BACKEND=file

# Verify install
RUN python -c "from tessera import Kernel; print('Tessera kernel imported OK')"

# CLI entry point
ENTRYPOINT ["tessera"]
CMD ["--help"]
