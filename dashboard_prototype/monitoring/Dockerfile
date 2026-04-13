# ═══════════════════════════════════════════════════════════════
# Monitoring — Custom Scripts / Exporters
# ═══════════════════════════════════════════════════════════════

FROM python:3.12-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (from pyproject.toml / uv.lock if they exist)
COPY pyproject.toml ./
# If there are no dependencies yet, this will just initialize the environment
RUN uv pip install --no-cache --system . || true

# Copy source code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Default command (placeholder, since this service is usually just configuration)
CMD ["python", "--version"]
