#!/bin/bash

# Build the guidance service image
docker build -t guidance-service -f Dockerfile.guidance .

# Run the guidance service container
docker run -d \
  --name guidance-service \
  -p 8085:8085 \
  -v $(pwd)/guidance.ttl:/app/guidance.ttl \
  -v $(pwd)/data:/app/data \
  guidance-service \
  conda run --no-capture-output -n ontology-framework python mcp_reference_server.py 