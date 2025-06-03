import subprocess
import sys
import os
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'bfg9k_mcp.py'))

# Minimal JSON-RPC request (adjust method as needed for your MCP)
REQUEST = {
    "jsonrpc": "2.0",
    "method": "listMethods",
    "id": 1
}


def test_mcp_stdio_probe():
    """Test that MCP process in stdio mode is alive and responsive."""
    env = os.environ.copy()
    env["BFG9K_DEBUG"] = "true"
    env["BFG9K_TRACE_LIFECYCLE"] = "true"
    env["BFG9K_USE_WASM"] = "false"

    logger.info(f"Starting MCP process: {MCP_PATH}")
    proc = subprocess.Popen(
        [sys.executable, MCP_PATH, "--debug"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=1
    )

    try:
        # Give the process a moment to start
        time.sleep(2)
        logger.info("Sending JSON-RPC request to MCP stdin...")
        proc.stdin.write(json.dumps(REQUEST) + "\n")
        proc.stdin.flush()

        # Read response (with timeout)
        logger.info("Waiting for response from MCP stdout...")
        start = time.time()
        response = ""
        while time.time() - start < 1:
            line = proc.stdout.readline()
            if line:
                logger.info(f"Received line: {line.strip()}")
                response += line
                try:
                    data = json.loads(line)
                    if data.get("id") == 1:
                        logger.info(f"Received valid JSON-RPC response: {data}")
                        break
                except Exception:
                    continue
        else:
            logger.error("No valid response received from MCP within timeout.")
            assert False, "No valid response from MCP"

        # Check process is still alive
        assert proc.poll() is None, "MCP process exited prematurely"
        logger.info("MCP process is alive and responsive.")
    finally:
        logger.info("Terminating MCP process...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        logger.info("MCP process terminated.")

if __name__ == "__main__":
    test_mcp_stdio_probe() 