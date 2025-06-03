from fastmcp import FastMCP

# Create the MCP server instance
mcp = FastMCP("BFG9K MCP SSE Example")

# Register a simple tool for demonstration
@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"

if __name__ == "__main__":
    # Run the server with SSE transport on port 8080
    mcp.run(transport="sse" host="0.0.0.0"
        port=8080) 