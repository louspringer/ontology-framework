
from bfg9k_manager import BFG9KManager
import os
import sys

def mcp_preflight():
    try:
        config_path = os.path.join(os.path.dirname(__file__), "bfg9k_config.ttl")
        manager = BFG9KManager(config_path)
        print("✅ BFG9KManager initialized successfully.")
        print(f"📡 Backend URL: {manager.base_url}")
        print(f"🗂️ Repository: {manager.repository}")
        return 0
    except Exception as e:
        print("❌ MCP Preflight check failed:")
        print(str(e))
        return 1

if __name__ == "__main__":
    sys.exit(mcp_preflight())
