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

# Create conda environment with minimal dependencies
RUN conda env create -f environment.yml && \
    conda clean -afy

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

# Copy all necessary files for package installation
COPY setup.py pyproject.toml README.md ./
COPY src/ontology_framework/ src/ontology_framework/
COPY guidance.ttl /app/guidance.ttl

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/ontologies /app/data/validation /app/data/visualization && \
    chmod -R 755 /app/data

# Set environment variables
ENV PYTHONPATH=/app/src \
    CONDA_DEFAULT_ENV=ontology-framework \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    MCP_PORT=8080

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Install the package and dependencies
RUN conda run -n ontology-framework pip install -e .

# Switch to non-root user
USER appuser

# Define volumes for persistent data
VOLUME ["/app/data"]

# Expose MCP port
EXPOSE 8080

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/mcp/health || exit 1

# Set the default command to run the MCP server with FastMCP
CMD ["sh", "-c", "echo 'Starting BFG9K MCP Server...' && \
    . /opt/conda/etc/profile.d/conda.sh && \
    conda activate ontology-framework && \
    echo 'Contents of /app/guidance.ttl:' && \
    cat /app/guidance.ttl && \
    echo 'Installed packages:' && \
    pip list && \
    echo 'Starting FastMCP...' && \
    python -m ontology_framework.mcp.bfg9k_mcp_server"]