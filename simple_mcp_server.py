import logging
from datetime import datetime
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP("Simple MCP Server")

@mcp.tool()
async def health() -> dict:
    """Health check tool for MCP server."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@mcp.tool()
async def validate_ontology(ontology_path: str) -> dict:
    """Dummy validation tool."""
    # TODO: Replace with your real validation logic
    logger.info(f"Validating ontology at {ontology_path}")
    return {"success": True, "ontology": ontology_path, "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    mcp.run(transport="sse", port=8080, host="127.0.0.1") 