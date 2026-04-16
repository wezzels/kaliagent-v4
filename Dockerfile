# Agentic AI - Production Docker Image
# Multi-stage build for minimal runtime image

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.12-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.12-slim as runtime

LABEL maintainer="Wesley Robbins <wlrobbi@gmail.com>"
LABEL version="0.7.0"
LABEL description="Agentic AI - Multi-Agent Orchestration Framework"

# Create non-root user for security
RUN groupadd --gid 1000 agentic && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home agentic

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=agentic:agentic agentic_ai/ ./agentic_ai/
COPY --chown=agentic:agentic tests/ ./tests/
COPY --chown=agentic:agentic README.md .
COPY --chown=agentic:agentic pytest.ini .

# Create directories for data
RUN mkdir -p /app/data /app/logs /app/config && \
    chown -R agentic:agentic /app

# Switch to non-root user
USER agentic

# Expose ports
# 5000: API server
# 8000: Metrics endpoint
EXPOSE 5000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AGENTIC_AI_ENV=production \
    AGENTIC_AI_LOG_LEVEL=INFO

# Default command
CMD ["python", "-m", "agentic_ai.server", "--host", "0.0.0.0", "--port", "5000"]
