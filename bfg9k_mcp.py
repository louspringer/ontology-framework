import logging
from datetime import datetime
from fastmcp import FastMCP
from bfg9k_manager import BFG9KManager
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP("BFG9K MCP Server")

# Create BFG9KManager instance
config_path = os.path.join(os.path.dirname(__file__), "bfg9k_config.ttl")
bfg9k = BFG9KManager(config_path)

def get_manager():
    # Helper to get a fresh manager if needed
    return bfg9k

@mcp.tool()
async def validate_guidance(content: str) -> dict:
    """Validate content against guidance ontology."""
    logger.info(f"Validating guidance content: {content[:60]}...")
    try:
        with open("temp_validation.ttl", "w") as f:
            f.write(content)
        result = get_manager().validate_ontology("temp_validation.ttl")
        if not isinstance(result, dict):
            result = {"raw_result": str(result)}
        return {"result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@mcp.tool()
async def query_guidance(sparql_query: str) -> dict:
    """Query guidance ontology."""
    logger.info(f"Querying guidance ontology: {sparql_query[:60]}...")
    try:
        result = get_manager().query_ontology(sparql_query)
        if not isinstance(result, dict):
            result = {"raw_result": str(result)}
        return {"result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Query failed: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@mcp.tool()
async def update_guidance(content: str) -> dict:
    """Update guidance ontology."""
    logger.info(f"Updating guidance ontology: {content[:60]}...")
    try:
        with open("temp_update.ttl", "w") as f:
            f.write(content)
        result = get_manager().update_ontology("temp_update.ttl")
        if not isinstance(result, dict):
            result = {"raw_result": str(result)}
        return {"result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Update failed: {e}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    mcp.run(transport="sse", port=8080, host="0.0.0.0") 