#!/bin/bash
set -e

echo "Starting BFG9K MCP Server (FastMCP 2.0) on port 8080..."
conda run -n ontology-framework python src/ontology_framework/mcp/bfg9k_mcp_server.py --port 8080 