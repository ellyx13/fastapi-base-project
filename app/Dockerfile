# ==========================
# Builder Stage
# ==========================
# That why I use the slim-bookworm image instead of the alpine image
# https://pythonspeed.com/articles/base-image-python-docker-images/
FROM python:3.12-slim-bookworm AS builder

WORKDIR /opt/projects/app

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc build-essential ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy only dependency files first (for better layer caching)
COPY pyproject.toml requirements.lock ./

# Create and install dependencies into venv
RUN uv venv /opt/venv \
    && uv pip install -r requirements.lock

# ==========================
# Final Stage
# ==========================
FROM python:3.12-slim-bookworm

WORKDIR /opt/projects/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Only keep runtime dependencies (no compiler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .