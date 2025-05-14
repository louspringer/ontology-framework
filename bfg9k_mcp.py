from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import logging
from datetime import datetime
from fastmcp import FastMCP
from bfg9k_manager import BFG9KManager
import os
import traceback
from monkey_patch import PatchedServerSession
from fix_prefixes import fix_prefixes
from turtle_validation import validate_all

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
        # Return all validation results, including OWLReady2 reasoning
        return {
            "result": result,
            "shacl_conforms": result.get("shacl_conforms"),
            "shacl_results": result.get("shacl_results"),
            "isomorphic": result.get("isomorphic"),
            "owlready2_consistent": result.get("owlready2_consistent"),
            "owlready2_inconsistencies": result.get("owlready2_inconsistencies"),
            "timestamp": datetime.now().isoformat()
        }
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
        with open("temp_update.ttl", "r") as f:
            debug_content = f.read()
        logger.debug(f"[update_guidance] Content of temp_update.ttl (first 500 chars): {debug_content[:500]}")
        result = get_manager().update_ontology("temp_update.ttl")
        logger.info(f"[update_guidance] Update result: {str(result)[:200]}")
        if not isinstance(result, dict):
            result = {"raw_result": str(result)}
        return {"result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"[update_guidance] Update failed: {e}")
        logger.error(traceback.format_exc())
        return {"error": str(e), "trace": traceback.format_exc(), "timestamp": datetime.now().isoformat()}

@mcp.tool()
async def fix_prefixes_tool(content: str, apply: bool = False) -> dict:
    """Fix relative and malformed prefixes in a Turtle file. Accepts a filename or raw Turtle content. Returns the changes it would make (dry-run by default)."""
    import os
    import tempfile
    import traceback
    import datetime
    try:
        # If content is a file path, use it directly
        if os.path.isfile(content):
            turtle_file = content
        else:
            # Write content to a temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ttl", mode="w") as tf:
                tf.write(content)
                turtle_file = tf.name
        changes = fix_prefixes(turtle_file, dry_run=not apply)
        return {
            "changes": changes,
            "applied": apply,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc(),
            "timestamp": datetime.datetime.now().isoformat()
        }

@mcp.tool()
async def validate_turtle_tool(content: str) -> dict:
    """Validate a Turtle file or raw Turtle content for common ontology issues. Returns a structured report."""
    import os
    import tempfile
    import datetime
    import traceback
    try:
        # If content is a file path, use it directly
        if os.path.isfile(content):
            turtle_file = content
        else:
            # Write content to a temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ttl", mode="w") as tf:
                tf.write(content)
                turtle_file = tf.name
        results = validate_all(turtle_file)
        return {
            "results": results,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc(),
            "timestamp": datetime.datetime.now().isoformat()
        }

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.debug("[main] Starting BFG9K MCP Server with SSE transport on 0.0.0.0:8080")
    mcp.run(transport="sse", port=8080, host="0.0.0.0") 