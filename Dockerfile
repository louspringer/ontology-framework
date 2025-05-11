# syntax=docker/dockerfile:1.4

# Build stage for conda environment
FROM continuumio/miniconda3:latest AS conda-builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    graphviz \
    graphviz-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only the files needed for environment setup
COPY environment.yml setup.py pyproject.toml README.md ./
COPY src/ontology_framework/__init__.py src/ontology_framework/

# Create conda environment (no BuildKit cache mounts for ACR)
RUN conda env create -f environment.yml && conda clean -afy

# Install FastAPI dependencies
RUN conda run -n ontology-framework pip install fastapi uvicorn

# Runtime stage
FROM continuumio/miniconda3:latest

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy conda environment from builder
COPY --from=conda-builder /opt/conda/envs/ontology-framework /opt/conda/envs/ontology-framework

# Copy project files and guidance.ttl
COPY . .
COPY guidance.ttl /app/guidance.ttl
COPY start.sh /app/start.sh

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/ontologies /app/data/validation /app/data/visualization && \
    chmod -R 755 /app/data

# Set environment variables
ENV PYTHONPATH=/app/src \
    CONDA_DEFAULT_ENV=ontology-framework \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    GRAPHDB_URL=http://graphdb:7200 \
    MCP_PORT=8080

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Define volumes for persistent data
VOLUME ["/app/data"]

# Expose ports for Python services
EXPOSE 8000 8080

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD conda run -n ontology-framework python -c "import requests; requests.get('http://localhost:8000/health')"

# Install the package in development mode
RUN conda run -n ontology-framework pip install -e .

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting BFG9K MCP Server..."\n\
conda run -n ontology-framework python src/ontology_framework/mcp/bfg9k_mcp_server.py &\n\
echo "Starting Validation Service..."\n\
conda run -n ontology-framework python src/ontology_framework/tools/validate_guidance.py &\n\
echo "Starting Ontology Framework..."\n\
conda run -n ontology-framework python src/ontology_framework/cli/main.py &\n\
echo "All services started. Waiting..."\n\
wait' > /app/start.sh && chmod +x /app/start.sh

# Set the default command to run all services
CMD ["/app/start.sh"]