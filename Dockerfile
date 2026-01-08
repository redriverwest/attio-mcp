FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install production dependencies
COPY pyproject.toml README.md ./
COPY attio_mcp ./attio_mcp

RUN pip install --upgrade pip \
    && pip install .

# Create non-root user for runtime
RUN useradd --create-home --shell /bin/bash appuser

USER appuser

# Default configuration values (override in production as needed)
ENV ATTIO_API_BASE_URL=https://api.attio.com/v2 \
    LOG_LEVEL=INFO

CMD ["python", "-m", "attio_mcp.server"]

