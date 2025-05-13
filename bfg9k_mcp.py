from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Dict, Any, List
import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from bfg9k_manager import BFG9KManager

class BFG9KMCPManager:
    def __init__(self, config_path: str = "bfg9k_config.ttl"):
        self.bfg9k = BFG9KManager(config_path)
        self.governance_rules = self.bfg9k.get_governance_rules()

    async def validate_guidance(self, content: str) -> Dict[str, Any]:
        """Validate content against guidance ontology"""
        # Create temporary file for validation
        with open("temp_validation.ttl", "w") as f:
            f.write(content)
        
        # Validate using BFG9K
        result = self.bfg9k.validate_ontology("temp_validation.ttl")
        return result

    async def query_guidance(self, sparql_query: str) -> Dict[str, Any]:
        """Query guidance ontology"""
        return self.bfg9k.query_ontology(sparql_query)

    async def update_guidance(self, content: str) -> Dict[str, Any]:
        """Update guidance ontology"""
        # Create temporary file for update
        with open("temp_update.ttl", "w") as f:
            f.write(content)
        
        # Update using BFG9K
        result = self.bfg9k.update_ontology("temp_update.ttl")
        return result

@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle."""
    # Initialize BFG9K manager
    manager = BFG9KMCPManager()
    try:
        yield {"manager": manager}
    finally:
        # Cleanup if needed
        pass

# Create server instance
server = Server("bfg9k-guidance-server", lifespan=server_lifespan)

@server.list_prompts()
async def handle_list_prompts() -> List[types.Prompt]:
    """List available guidance prompts"""
    return [
        types.Prompt(
            name="validate-guidance",
            description="Validate content against guidance ontology",
            arguments=[
                types.PromptArgument(
                    name="content",
                    description="Turtle content to validate",
                    required=True
                )
            ],
        ),
        types.Prompt(
            name="query-guidance",
            description="Query guidance ontology",
            arguments=[
                types.PromptArgument(
                    name="sparql",
                    description="SPARQL query to execute",
                    required=True
                )
            ],
        ),
        types.Prompt(
            name="update-guidance",
            description="Update guidance ontology",
            arguments=[
                types.PromptArgument(
                    name="content",
                    description="Turtle content to update",
                    required=True
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: Dict[str, str] | None
) -> types.GetPromptResult:
    """Get prompt template"""
    if name not in ["validate-guidance", "query-guidance", "update-guidance"]:
        raise ValueError(f"Unknown prompt: {name}")

    return types.GetPromptResult(
        description=f"BFG9K Guidance {name.replace('-', ' ').title()}",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Execute {name} with arguments: {arguments}"
                ),
            )
        ],
    )

@server.call_tool()
async def handle_validate_guidance(
    name: str, arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate content against guidance"""
    ctx = server.request_context
    manager = ctx.lifespan_context["manager"]
    return await manager.validate_guidance(arguments["content"])

@server.call_tool()
async def handle_query_guidance(
    name: str, arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """Query guidance ontology"""
    ctx = server.request_context
    manager = ctx.lifespan_context["manager"]
    return await manager.query_guidance(arguments["sparql"])

@server.call_tool()
async def handle_update_guidance(
    name: str, arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """Update guidance ontology"""
    ctx = server.request_context
    manager = ctx.lifespan_context["manager"]
    return await manager.update_guidance(arguments["content"])

async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="bfg9k-guidance",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(run()) 