import os
import sys
from pathlib import Path

# Add src to Python path before other imports
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from typing import Any, Dict
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import logging
from datetime import datetime
from fastmcp import FastMCP
from bfg9k_manager import BFG9KManager
import traceback
from monkey_patch import PatchedServerSession
from fix_prefixes import fix_prefixes
from turtle_validation import validate_all
import asyncio
import tempfile
import json
import argparse
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

def update_mcp_config():
    """Update .cursor/mcp.json with absolute paths discovered at runtime."""
    try:
        # Get absolute paths
        project_root = Path(__file__).parent.absolute()
        python_path = sys.executable
        bfg9k_script = project_root / "bfg9k_mcp.py"
        src_path = project_root / "src"
        
        # Create the MCP config directory if it doesn't exist
        mcp_dir = project_root / ".cursor"
        mcp_dir.mkdir(exist_ok=True)
        
        # Create/update the MCP config with absolute paths
        mcp_config = {
            "mcpServers": {
                "bfg9k": {
                    "command": str(python_path),
                    "args": [
                        str(bfg9k_script)
                    ],
                    "env": {
                        "PYTHONPATH": str(src_path)
                    }
                },
                "datapilot": {
                    "url": "http://localhost:7700/sse",
                    "type": "sse"
                }
            }
        }
        
        # Write the config
        config_path = mcp_dir / "mcp.json"
        with open(config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
            
        print(f"Updated MCP configuration at {config_path}")
        print(f"Using Python: {python_path}")
        print(f"BFG9K script: {bfg9k_script}")
        print(f"PYTHONPATH: {src_path}")
        return True
    except Exception as e:
        print(f"Error updating MCP configuration: {e}")
        print(f"Project root: {project_root}")
        print(f"Python path: {sys.executable}")
        return False

def check_mcp_config():
    """Validate .cursor/mcp.json and log any perceived misconfiguration, including GraphDB endpoint URL."""
    import logging
    config_path = Path(__file__).parent / ".cursor" / "mcp.json"
    logger = logging.getLogger("mcp_config_check")
    if not config_path.exists():
        logger.error(f"MCP config file not found: {config_path}")
        return False
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        # Check for required structure
        servers = config.get("mcpServers", {})
        bfg9k = servers.get("bfg9k", {})
        if not bfg9k:
            logger.error("No 'bfg9k' server config found in mcp.json.")
            return False
        command = bfg9k.get("command")
        args = bfg9k.get("args", [])
        env = bfg9k.get("env", {})
        if not command or not Path(command).exists():
            logger.error(f"'command' path is missing or does not exist: {command}")
        if not args or not Path(args[0]).exists():
            logger.error(f"'args[0]' (script) path is missing or does not exist: {args}")
        if not env.get("PYTHONPATH") or not Path(env["PYTHONPATH"]).exists():
            logger.error(f"'PYTHONPATH' is missing or does not exist: {env.get('PYTHONPATH')}")
        # Optionally, check for datapilot config
        datapilot = servers.get("datapilot", {})
        if not datapilot.get("url"):
            logger.warning("No 'url' found for 'datapilot' in mcp.json.")
        # Check for GraphDB endpoint URL in config or environment
        graphdb_url = os.environ.get("GRAPHDB_URL")
        if not graphdb_url:
            # Try to find in config (if you store it there)
            graphdb_url = config.get("graphdb_url") or env.get("GRAPHDB_URL")
        if graphdb_url:
            logger.info(f"GraphDB endpoint URL: {graphdb_url}")
        else:
            logger.error("No GraphDB endpoint URL found in environment or config. Set GRAPHDB_URL in your environment or config.")
        logger.info("MCP config validation complete.")
        return True
    except Exception as e:
        logger.error(f"Error reading or parsing mcp.json: {e}")
        return False

if __name__ == "__main__":
    # Boot check for MCP config
    check_mcp_config()
    parser = argparse.ArgumentParser(description="BFG9K MCP Server")
    parser.add_argument("--update-config", action="store_true", help="Update .cursor/mcp.json configuration")
    args = parser.parse_args()
    
    if args.update_config:
        if update_mcp_config():
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Start the MCP server
    mcp.run()
