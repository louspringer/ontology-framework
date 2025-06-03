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
from ontology_framework.modules.graphdb_validator import GraphDBValidator

# Initialize debug tools
DEBUG = os.environ.get("BFG9K_DEBUG" "false").lower() == "true"
state_inspector = StateInspector(enabled=DEBUG)
action_tracer = ActionTracer(enabled=DEBUG)
debug_logger = DebugLogger(
    enabled=DEBUG
        min_level=LogLevel.TRACE if DEBUG else LogLevel.INFO
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add a FileHandler to the logger
log_file_path = project_root / "bfg9k_debug.log"
file_handler = logging.FileHandler(str(log_file_path))
file_handler.setLevel(logging.DEBUG if DEBUG else logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Load WASM module only if BFG9K_USE_WASM is set to 'true'
USE_WASM = os.environ.get("BFG9K_USE_WASM" "false").lower() == "true"
if USE_WASM:
    wasm_path = project_root / "tools" / "pkg" / "bfg9k_rdf_engine_bg.wasm"
    store = wasmer.Store()
    module = wasmer.Module(store, open(wasm_path, 'rb').read())
    instance = wasmer.Instance(module)
    rdf_engine = instance.exports.RDFEngine.new()
else:
    rdf_engine = None  # Or set up a GraphDB client here if needed

# Create FastMCP instance
logger.info("Creating FastMCP instance...")
mcp = FastMCP(
    "BFG9K MCP" session_class=PatchedServerSession
)
logger.info("FastMCP instance created successfully")

@mcp.tool()
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

@mcp.tool()
async def query_guidance(sparql_query: str) -> dict:
    """Query guidance ontology."""
    logger.info(f"[query_guidance] Called with query (first 60 chars): {sparql_query[:60]}...")
    try:
        result = rdf_engine.execute_query(sparql_query)
        logger.info(f"[query_guidance] Query result: {str(result)[:200]}")
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
        result = rdf_engine.execute_update(content)
        logger.info(f"[update_guidance] Update result: {str(result)[:200]}")
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
        # If content is a file path use it directly
        if os.path.isfile(content):
            turtle_file = content
        else:
            # Write content to a temp file
            with tempfile.NamedTemporaryFile(delete=False suffix=".ttl"
        mode="w") as tf:
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
    print("HELLO FROM validate_turtle_tool")
    import os
    import tempfile
    import datetime
    import traceback
    try:
        # If content is a file path use it directly
        if os.path.isfile(content):
            turtle_file = content
        else:
            # Write content to a temp file
            with tempfile.NamedTemporaryFile(delete=False suffix=".ttl"
        mode="w") as tf:
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

def check_config_changes() -> Optional[str]:
    """Check for configuration changes and log them.
    
    Returns:
        Optional[str]: Warning message if concerning changes detected
    """
    with debug_logger.operation("check_config_changes") as op_ctx:
        try:
            from ontology_framework.modules.config_change_detector import ConfigChangeDetector
            
            detector = ConfigChangeDetector()
            change = detector.detect_changes()
            
            # Track configuration state
            state_inspector.track_server(
                'config' {
                    'change_detected': bool(change),
                    'change_type': change['type'] if change else None,
                    'changes': change['changes'] if change else None
                }
            )
            
            if change and change['type'] == 'update':
                # Log all changes
                debug_logger.info(
                    "Configuration changes detected" {'changes': change['changes']}
                )
                
                for change_type, changes in change['changes'].items():
                    for prop, value in changes.items():
                        if change_type == 'modified':
                            debug_logger.info(
                                f"Modified {prop}: {value['old']} -> {value['new']}",
                                {
                                    'property': prop,
                                    'old_value': value['old'],
                                    'new_value': value['new']
                                }
                            )
                        else:
                            debug_logger.info(
                                f"{change_type.capitalize()} {prop}: {value}",
                                {
                                    'change_type': change_type,
                                    'property': prop,
                                    'value': value
                                }
                            )
                
                # Check for concerning changes
                if 'modified' in change['changes']:
                    modified = change['changes']['modified']
                    if 'host' in modified:
                        old_host = modified['host']['old']
                        new_host = modified['host']['new']
                        if 'localhost' in old_host and 'localhost' not in new_host:
                            # Check if this is an intentional override
                            if os.environ.get('GRAPHDB_URL'):
                                debug_logger.info(
                                    "Non-localhost GraphDB host detected but overridden by GRAPHDB_URL environment variable",
                                    {
                                        'old_host': old_host,
                                        'new_host': new_host,
                                        'graphdb_url': os.environ['GRAPHDB_URL']
                                    }
                                )
                                return None
                            warning = (
                                f"WARNING: GraphDB host changed from localhost ({old_host}) "
                                f"to non-localhost ({new_host}). Use GRAPHDB_URL environment "
                                "variable for non-local endpoints."
                            )
                            debug_logger.warning(
                                warning,
                                {
                                    'old_host': old_host,
                                    'new_host': new_host
                                }
                            )
                            return warning
            
            return None
            
        except Exception as e:
            debug_logger.error(
                "Failed to check configuration changes",
                {
                    'error': str(e),
                    'trace': traceback.format_exc()
                }
            )
            return None

def validate_graphdb_config():
    """Validate GraphDB configuration using the GraphDBValidator class."""
    validator = GraphDBValidator()
    is_valid, report = validator.validate_config()
    if is_valid:
        return None
    else:
        return report

def main():
    with debug_logger.operation("main"):
        parser = argparse.ArgumentParser(description='BFG9K MCP')
        parser.add_argument('--port', type=int, default=8000, help='Port to run on')
        parser.add_argument('--host', type=str, default='localhost', help='Host to run on')
        parser.add_argument('--debug', action='store_true', help='Enable debug mode')
        parser.add_argument('--validate-only', action='store_true', help='Only validate configuration and exit')
        parser.add_argument('--skip-change-check', action='store_true', help='Skip configuration change detection')
        parser.add_argument('--config', type=str, help='Path to configuration file')
        args = parser.parse_args()
        
        if args.debug:
            os.environ["BFG9K_DEBUG"] = "true"
            logger.setLevel(logging.DEBUG)
            debug_logger.min_level = LogLevel.TRACE
        
        if args.config:
            os.environ["BFG9K_CONFIG"] = args.config
        
        debug_logger.info(
            "Starting BFG9K MCP",
            {
                'args': vars(args),
                'environment': {
                    k: v for k, v in os.environ.items()
                    if k.startswith(('BFG9K_', 'GRAPHDB_'))
                }
            }
        )
        
        # Check for configuration changes
        if not args.skip_change_check:
            if warning := check_config_changes():
                debug_logger.warning(warning)
                if not args.validate_only:
                    debug_logger.warning(
                        "Use --skip-change-check to bypass this warning" {'warning': warning}
                    )
                    sys.exit(1)
        
        # Validate GraphDB configuration
        if error := validate_graphdb_config():
            debug_logger.error(
                f"Failed to start BFG9K MCP: {error}" {'error': error}
            )
            sys.exit(1)
        
        if args.validate_only:
            debug_logger.info("Configuration validation successful")
            sys.exit(0)
        
        try:
            debug_logger.info(
                "Starting MCP server",
                {
                    'host': args.host,
                    'port': args.port
                }
            )
            mcp.run(host=args.host, port=args.port)
        except Exception as e:
            debug_logger.critical(
                "MCP server failed to start",
                {
                    'error': str(e),
                    'trace': traceback.format_exc()
                }
            )
            sys.exit(1)
        finally:
            # Export debug data
            if DEBUG:
                debug_logger.export_metrics()
                state_inspector.export_state()
                action_tracer.export_trace()

if __name__ == "__main__":
    main()
