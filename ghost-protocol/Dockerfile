# ⚔️ GHOST PROTOCOL — DOCKERFILE
# Multi-stage build for minimal attack surface

FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir --user -r requirements.txt

# ============================================

FROM python:3.12-slim

WORKDIR /ghost

# Runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    sqlite3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled Python packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /ghost/{config,core,storage,queue,auth,sandbox,adapters,agents,models,templates,results}

# Default command
CMD ["python3", "-m", "core.ghost_orchestrator"]