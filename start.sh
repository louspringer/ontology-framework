#!/bin/bash
set -e

echo "Starting BFG9K MCP Server (FastMCP 2.0) on port 8080..."
conda run -n ontology-framework python bfg9k_mcp.py --port 8080 