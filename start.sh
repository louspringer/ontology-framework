#!/bin/bash
set -e

# Start BFG9K MCP Server on port 8000
( conda run -n ontology-framework python src/ontology_framework/mcp/bfg9k_mcp_server.py > /app/bfg9k_mcp_server.log 2>&1 & )
echo "Started BFG9K MCP Server on port 8000 (log: /app/bfg9k_mcp_server.log)"

# Start Validation Service (if needed)
# conda run -n ontology-framework python src/ontology_framework/tools/validate_guidance.py &

# Start Ontology Framework CLI (if needed)
# conda run -n ontology-framework python src/ontology_framework/cli/main.py &

# Start FastMCP MCP Server on port 8080 (in foreground, log to file)
echo "Starting FastMCP MCP Server on port 8080..."
conda run -n ontology-framework python src/ontology_framework/mcp/mcp_server.py --port 8080 | tee /app/mcp_server.log

# Wait for background processes
wait 