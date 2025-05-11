# syntax=docker/dockerfile:1.4

# Build stage for conda environment
FROM --platform=$BUILDPLATFORM continuumio/miniconda3:latest AS conda-builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    graphviz \
    graphviz-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only the files needed for environment setup
COPY --link environment.yml setup.py pyproject.toml README.md ./
COPY --link src/ontology_framework/__init__.py src/ontology_framework/

# Create conda environment with improved caching and memory limits
RUN --mount=type=cache,target=/opt/conda/pkgs \
    --mount=type=cache,target=/root/.cache/pip \
    conda env create -f environment.yml && \
    conda clean -afy

# Runtime stage
FROM --platform=$TARGETPLATFORM continuumio/miniconda3:latest

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy conda environment from builder
COPY --from=conda-builder --link /opt/conda/envs/ontology-framework /opt/conda/envs/ontology-framework

# Copy project files
COPY --link . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/ontologies /app/data/validation /app/data/visualization && \
    chmod -R 755 /app/data

# Set environment variables
ENV PYTHONPATH=/app/src \
    CONDA_DEFAULT_ENV=ontology-framework \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Define volumes for persistent data
VOLUME ["/app/data"]

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD conda run -n ontology-framework python -c "import requests; requests.get('http://localhost:8000/health')"

# Install the package in development mode
RUN conda run -n ontology-framework pip install -e .

# Set the default command
CMD ["conda", "run", "-n", "ontology-framework", "python", "bfg9k_mcp_server.py"]