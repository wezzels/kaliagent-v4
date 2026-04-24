# KaliAgent v4 - Production Docker Image
# Multi-stage build for minimal attack surface

FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Production image
FROM python:3.11-slim

LABEL maintainer="KaliAgent Team"
LABEL version="4.0.0"
LABEL description="Automated Penetration Testing Platform"

# Security: Run as non-root user
RUN groupadd -r kaliagent && useradd -r -g kaliagent kaliagent

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    nmap \
    sqlmap \
    aircrack-ng \
    wireshark \
    tcpdump \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy wheels from builder and install
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copy application code
COPY --chown=kaliagent:kaliagent . /app

# Create directories for reports, recordings, data
RUN mkdir -p /app/reports /app/recordings /app/data \
    && chown -R kaliagent:kaliagent /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV KALIAGENT_VERSION=4.0.0
ENV KALIAGENT_ENV=production

# Switch to non-root user
USER kaliagent

# Expose dashboard port
EXPOSE 5007

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5007/health || exit 1

# Default command
CMD ["python", "phase6/dashboard_v2.py"]
