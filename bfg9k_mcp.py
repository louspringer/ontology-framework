import logging
from datetime import datetime
from fastmcp import FastMCP
from bfg9k_manager import BFG9KManager
import os
import traceback
from monkey_patch import PatchedServerSession

# Configure logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP(
    "BFG9K MCP",
    session_class=PatchedServerSession
)

# Create BFG9KManager instance
print("Current working directory:", os.getcwd())
config_path = os.path.join(os.path.dirname(__file__), "bfg9k_config.ttl")
print("Config path:", config_path)
bfg9k = BFG9KManager(config_path)

def get_manager():
    # Helper to get a fresh manager if needed
    logger.debug("Getting BFG9KManager instance")
    return bfg9k

@mcp.tool()
async def validate_guidance(content: str) -> dict:
    """Validate content against guidance ontology. Accepts either a filename or raw Turtle content."""
    logger.info(f"[validate_guidance] ENTRY: called with content (first 60 chars): {content[:60]}...")
    try:
        # Check if 'content' is a path to an existing file
        if os.path.isfile(content):
            with open(content, "r") as infile:
                turtle_content = infile.read()
            logger.debug(f"[validate_guidance] Read Turtle content from file: {content}")
        else:
            turtle_content = content
            logger.debug("[validate_guidance] Treating input as raw Turtle content")
        with open("temp_validation.ttl", "w") as f:
            f.write(turtle_content)
        logger.debug("[validate_guidance] Wrote content to temp_validation.ttl")
        result = get_manager().validate_ontology("temp_validation.ttl")
        logger.info(f"[validate_guidance] Validation result: {str(result)[:200]}")
        if not isinstance(result, dict):
            result = {"raw_result": str(result)}
        logger.info(f"[validate_guidance] RETURN: {result}")
        return {"result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"[validate_guidance] Validation failed: {e}")
        logger.error(traceback.format_exc())
        logger.info(f"[validate_guidance] RETURN ERROR: {str(e)}")
        return {"error": str(e), "trace": traceback.format_exc(), "timestamp": datetime.now().isoformat()}

@mcp.tool()
async def query_guidance(sparql_query: str) -> dict:
    """Query guidance ontology."""
    logger.info(f"[query_guidance] Called with query (first 60 chars): {sparql_query[:60]}...")
    try:
        result = get_manager().query_ontology(sparql_query)
        logger.info(f"[query_guidance] Query result: {str(result)[:200]}")
        if not isinstance(result, dict):
            result = {"raw_result": str(result)}
        return {"result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"[query_guidance] Query failed: {e}")
        logger.error(traceback.format_exc())
        return {"error": str(e), "trace": traceback.format_exc(), "timestamp": datetime.now().isoformat()}

@mcp.tool()
async def update_guidance(content: str) -> dict:
    """Update guidance ontology."""
    logger.info(f"[update_guidance] Called with content (first 60 chars): {content[:60]}...")
    try:
        with open("temp_update.ttl", "w") as f:
            f.write(content)
        logger.debug("[update_guidance] Wrote content to temp_update.ttl")
        result = get_manager().update_ontology("temp_update.ttl")
        logger.info(f"[update_guidance] Update result: {str(result)[:200]}")
        if not isinstance(result, dict):
            result = {"raw_result": str(result)}
        return {"result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"[update_guidance] Update failed: {e}")
        logger.error(traceback.format_exc())
        return {"error": str(e), "trace": traceback.format_exc(), "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.debug("[main] Starting BFG9K MCP Server with SSE transport on 0.0.0.0:8080")
    mcp.run(transport="sse", port=8080, host="0.0.0.0") 