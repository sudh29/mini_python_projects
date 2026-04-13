# ═══════════════════════════════════════════════════════════════
# Backend — FastAPI + Celery
# ═══════════════════════════════════════════════════════════════

FROM ghcr.io/astral-sh/uv:latest AS uv
FROM docker.io/library/python:3.12-slim

# Install uv for fast dependency management
COPY --from=uv /uv /uvx /bin/

WORKDIR /app

# Install system dependencies (needed for psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies using uv for speed and reliability
# We use --system to install directly into the system python environment
# instead of a virtualenv within the container.
COPY requirements.txt .
RUN uv pip install --no-cache --system -r requirements.txt

# Copy application code
COPY . .

# Create artifacts and logs directory
RUN mkdir -p /app/artifacts /app/logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port (default for FastAPI)
EXPOSE 8000

# The default command is for the API server.
# Overridden in docker-compose.yml for the Celery worker.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
