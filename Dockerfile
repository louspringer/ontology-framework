FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    graphviz \
    graphviz-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy environment file
COPY environment.yml .

# Copy project files
COPY . .

# Create conda environment and install dependencies
RUN conda env create -f environment.yml && \
    conda init bash && \
    . /opt/conda/etc/profile.d/conda.sh && \
    conda activate ontology-framework && \
    pip install uvicorn fastapi fastapi-mcp

# Download spacy model
SHELL ["conda", "run", "-n", "ontology-framework", "/bin/bash", "-c"]
RUN python -m spacy download en_core_web_md

# Create directories for data
RUN mkdir -p /app/data /app/temp_embeddings

# Set environment variables
ENV PYTHONPATH=/app/src

# Define volumes for persistent data
VOLUME ["/app/data", "/app/temp_embeddings"]

# Make port 8080 available
EXPOSE 8080

# Copy entrypoint.sh and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Activate conda environment and run the server
ENTRYPOINT ["/entrypoint.sh"]