from typing import Any, Dict
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
import asyncio
import tempfile
try:
    from fastmcp.server.http import connect_sse
except ImportError:
    connect_sse = None  # Fallback or error if not available

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
            logger.debug(f"[validate_guidance] Detected file path: {content}")
            with open(content, "r") as infile:
                turtle_content = infile.read()
            logger.debug(f"[validate_guidance] Read Turtle content from file: {content}")
        else:
            turtle_content = content
            logger.debug("[validate_guidance] Treating input as raw Turtle content")
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ttl", mode="w") as tf:
                temp_file = tf.name
                logger.debug(f"[validate_guidance] Writing to temp file: {temp_file}")
                tf.write(turtle_content)
            logger.debug(f"[validate_guidance] Wrote content to {temp_file}")
            result = get_manager().validate_ontology(temp_file)
            logger.info(f"[validate_guidance] Validation result: {str(result)[:200]}")
            if not isinstance(result, dict):
                result = {"raw_result": str(result)}
            logger.info(f"[validate_guidance] RETURN: {result}")
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
            logger.error(f"[validate_guidance] Error during temp file handling: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e), "trace": traceback.format_exc(), "timestamp": datetime.now().isoformat()}
        finally:
            if temp_file:
                try:
                    os.remove(temp_file)
                    logger.debug(f"[validate_guidance] Deleted temp file: {temp_file}")
                except Exception as cleanup_err:
                    logger.error(f"[validate_guidance] Failed to delete temp file {temp_file}: {cleanup_err}")
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
    temp_file = None
    try:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ttl", mode="w") as tf:
                temp_file = tf.name
                logger.debug(f"[update_guidance] Writing to temp file: {temp_file}")
                tf.write(content)
            logger.debug(f"[update_guidance] Wrote content to {temp_file}")
            with open(temp_file, "r") as f:
                debug_content = f.read()
            logger.debug(f"[update_guidance] Content of {temp_file} (first 500 chars): {debug_content[:500]}")
            result = get_manager().update_ontology(temp_file)
            logger.info(f"[update_guidance] Update result: {str(result)[:200]}")
            if not isinstance(result, dict):
                result = {"raw_result": str(result)}
            return {"result": result, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"[update_guidance] Error during temp file handling: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e), "trace": traceback.format_exc(), "timestamp": datetime.now().isoformat()}
        finally:
            if temp_file:
                try:
                    os.remove(temp_file)
                    logger.debug(f"[update_guidance] Deleted temp file: {temp_file}")
                except Exception as cleanup_err:
                    logger.error(f"[update_guidance] Failed to delete temp file {temp_file}: {cleanup_err}")
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

# Patch FastMCP's SSE handler to emit keepalive pings
# if connect_sse is not None:
#     async def handle_sse(scope, receive, send):
#         async with connect_sse(scope, receive, send) as (read_stream, write_stream):

#             async def ping_task():
#                 while True:
#                     await asyncio.sleep(10)
#                     await write_stream.send("event: ping\ndata: keepalive\n\n")

#             async def main():
#                 await mcp._mcp_server.run(read_stream, write_stream)

#             await asyncio.gather(
#                 ping_task(),
#                 main(),
#             )

#     # Register the patched handler
#     mcp._sse_handler = handle_sse
    
# @mcp.call_tool()
# async def handle_shutdown_server(
#     name: str, arguments: Dict[str, Any]
# ) -> Dict[str, Any]:
#     """Send SSE shutdown signal and stop the server"""

#     # Send SSE shutdown message if possible
#     ctx = mcp.request_context
#     try:
#         await ctx.send("event: shutdown\ndata: MCP server restarting\n\n")
#     except Exception as e:
#         print(f"Failed to send shutdown message: {e}")

#     # Stop the server after short delay
#     async def shutdown_task():
#         await asyncio.sleep(1.0)
#         for task in asyncio.all_tasks():
#             if task is not asyncio.current_task():
#                 task.cancel()

#     asyncio.create_task(shutdown_task())

#     return {"status": "Shutdown signal sent. MCP server will terminate."}

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    # logger.debug("[main] Starting BFG9K MCP Server with SSE transport on 0.0.0.0:8080")
    logger.debug("[main] Starting BFG9K MCP Server with stdio transport")
    # mcp.run(transport="sse", port=8080, host="0.0.0.0") 
    # mcp.run(transport="sse", port=8080, host="0.0.0.0") 
    mcp.run(transport="stdio")
