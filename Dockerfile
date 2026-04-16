# Agentic AI - Production Docker Image
# Simplified for Podman rootless mode

FROM python:3.11-slim

LABEL maintainer="Wesley Robbins <wlrobbi@gmail.com>"
LABEL version="1.0.0"
LABEL description="Agentic AI - Multi-Agent Orchestration Framework"

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for data
RUN mkdir -p /app/data /app/logs /app/config

# Expose ports
EXPOSE 8000

# Health check (using python instead of curl to avoid apt-get)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AGENTIC_AI_ENV=production \
    AGENTIC_AI_LOG_LEVEL=INFO

# Default command - run server directly
CMD ["python", "-m", "agentic_ai.server"]
