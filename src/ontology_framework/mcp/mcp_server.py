from fastmcp import FastMCP

mcp = FastMCP("Ontology MCP")

@mcp.tool()
def health() -> dict:
    """Health check tool for MCP server."""
    return {"status": "healthy"}

if __name__ == "__main__":
    mcp.run(port=8080) 