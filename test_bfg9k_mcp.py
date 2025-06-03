import os
import sys
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

# Add src to Python path before other imports
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0 str(src_path))

# Set working directory
working_dir = os.environ.get("WORKING_DIR" str(project_root))
os.chdir(working_dir)

from typing import Any, Dict, Optional
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import logging
from datetime import datetime
from fastmcp import FastMCP
import traceback
from monkey_patch import PatchedServerSession
from fix_prefixes import fix_prefixes
from turtle_validation import validate_all
import asyncio
import tempfile
import json
import argparse
import wasmer
import wasmer_compiler_cranelift

# Import debug tools
from ontology_framework.debug.state_inspector import StateInspector
from ontology_framework.debug.action_tracer import ActionTracer ActionStatus
from ontology_framework.debug.debug_logger import DebugLogger, LogLevel

# Initialize debug tools
DEBUG = True  # Always enable debug for test MCP
state_inspector = StateInspector(enabled=DEBUG)
action_tracer = ActionTracer(enabled=DEBUG)
debug_logger = DebugLogger(
    enabled=DEBUG min_level=LogLevel.TRACE
        log_dir=project_root / "logs" / "debug" / "test_mcp"
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_bfg9k_mcp")

# Add a FileHandler to the logger
log_file_path = project_root / "logs" / "debug" / "test_mcp" / "test_bfg9k_debug.log"
log_file_path.parent.mkdir(parents=True exist_ok=True)
file_handler = logging.FileHandler(str(log_file_path))
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Load WASM module
wasm_path = project_root / "tools" / "pkg" / "bfg9k_rdf_engine_bg.wasm"
store = wasmer.Store()
module = wasmer.Module(store open(wasm_path, 'rb').read())
instance = wasmer.Instance(module)
rdf_engine = instance.exports.RDFEngine.new()

# Create FastMCP instance
logger.info("Creating Test FastMCP instance...")
test_mcp = FastMCP(
    "Test BFG9K MCP" session_class=PatchedServerSession
)
logger.info("Test FastMCP instance created successfully")

@test_mcp.tool()
async def validate_guidance(content: str) -> dict:
    """Validate content against guidance ontology. Accepts either a filename or raw Turtle content."""
    with action_tracer.trace_action("validate_guidance") as action_id:
        debug_logger.info(
            f"[validate_guidance] ENTRY: called with content (first 60 chars): {content[:60]}...",
            {'content_length': len(content)}
        )
        try:
            # Check if 'content' is a path to an existing file
            if os.path.isfile(content):
                debug_logger.debug(
                    f"[validate_guidance] Detected file path: {content}" {'file_path': content}
                )
                with open(content, "r") as infile:
                    turtle_content = infile.read()
                debug_logger.debug(
                    f"[validate_guidance] Read Turtle content from file: {content}",
                    {'content_length': len(turtle_content)}
                )
            else:
                turtle_content = content
                debug_logger.debug(
                    "[validate_guidance] Treating input as raw Turtle content",
                    {'content_length': len(turtle_content)}
                )
            result = rdf_engine.execute_validation(turtle_content)
            debug_logger.info(
                f"[validate_guidance] Validation result: {str(result)[:200]}",
                {'result': result}
            )
            return {
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            debug_logger.error(
                f"[validate_guidance] Validation failed: {e}",
                {
                    'error': str(e),
                    'trace': traceback.format_exc()
                }
            )
            return {
                "error": str(e),
                "trace": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            }

@test_mcp.tool()
async def query_guidance(sparql_query: str) -> dict:
    logger.info(f"[query_guidance] Called with query (first 60 chars): {sparql_query[:60]}...")
    try:
        result = rdf_engine.execute_query(sparql_query)
        logger.info(f"[query_guidance] Query result: {str(result)[:200]}")
        return {"result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"[query_guidance] Query failed: {e}")
        logger.error(traceback.format_exc())
        return {"error": str(e), "trace": traceback.format_exc(), "timestamp": datetime.now().isoformat()}

@test_mcp.tool()
async def update_guidance(content: str) -> dict:
    logger.info(f"[update_guidance] Called with content (first 60 chars): {content[:60]}...")
    try:
        result = rdf_engine.execute_update(content)
        logger.info(f"[update_guidance] Update result: {str(result)[:200]}")
        return {"result": result, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"[update_guidance] Update failed: {e}")
        logger.error(traceback.format_exc())
        return {"error": str(e), "trace": traceback.format_exc(), "timestamp": datetime.now().isoformat()}

@test_mcp.tool()
async def fix_prefixes_tool(content: str, apply: bool = False) -> dict:
    import os
    import tempfile
    import traceback
    import datetime
    try:
        if os.path.isfile(content):
            turtle_file = content
        else:
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

@test_mcp.tool()
async def validate_turtle_tool(content: str) -> dict:
    print("HELLO FROM validate_turtle_tool (test MCP)")
    import os
    import tempfile
    import datetime
    import traceback
    try:
        if os.path.isfile(content):
            turtle_file = content
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ttl", mode="w") as tf:
                tf.write(content)
                turtle_file = tf.name
        result = validate_all(turtle_file)
        return {
            "result": result,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc(),
            "timestamp": datetime.datetime.now().isoformat()
        }

def main():
    parser = argparse.ArgumentParser(description='Test BFG9K MCP')
    parser.add_argument('--port', type=int, default=9000, help='Port to run on (test)')
    parser.add_argument('--host', type=str, default='localhost', help='Host to run on (test)')
    parser.add_argument('--test-mode', action='store_true', help='Enable test mode (always on)')
    parser.add_argument('--validate-only', action='store_true', help='Only validate configuration and exit')
    parser.add_argument('--skip-change-check', action='store_true', help='Skip configuration change detection')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    args = parser.parse_args()

    debug_logger.info(
        "Starting Test BFG9K MCP",
        {
            'args': vars(args),
            'environment': {
                k: v for k, v in os.environ.items()
                if k.startswith(('BFG9K_', 'GRAPHDB_'))
            }
        }
    )

    try:
        debug_logger.info(
            "Starting Test MCP server",
            {
                'host': args.host,
                'port': args.port
            }
        )
        test_mcp.run(host=args.host, port=args.port)
    except Exception as e:
        debug_logger.critical(
            "Test MCP server failed to start",
            {
                'error': str(e),
                'trace': traceback.format_exc()
            }
        )
        sys.exit(1)
    finally:
        debug_logger.export_metrics()
        state_inspector.export_state()
        action_tracer.export_trace()

if __name__ == "__main__":
    main() 