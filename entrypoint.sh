#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate ontology-framework
exec uvicorn bfg9k_mcp_server:app --host 0.0.0.0 --port 8080 