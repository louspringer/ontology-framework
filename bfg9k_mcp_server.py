from fastapi import FastAPI, Request
from fastapi_mcp import FastApiMCP
from bfg9k_manager import BFG9KManager
import json
import logging
from typing import Dict, Any, Optional
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD
from sse_starlette.sse import EventSourceResponse
import asyncio
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.background import BackgroundTask

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='mcp.log'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BFG9K Guidance Server",
    description="The Big Friendly Guidance 9000 - Ultimate firepower for ontology validation and management."
)

# Initialize BFG9K manager
bfg9k = BFG9KManager()

@app.post("/validate_guidance", operation_id="validate_guidance")
async def validate_guidance(content: str) -> Dict[str, Any]:
    """Validate content against guidance ontology."""
    try:
        logger.debug(f"Validating content: {content[:100]}...")
        with open("temp_validation.ttl", "w") as f:
            f.write(content)
        result = bfg9k.validate_ontology("temp_validation.ttl")
        logger.debug(f"Validation result: {result}")
        return {"result": result}
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return {"error": str(e)}

@app.post("/query_guidance", operation_id="query_guidance")
async def query_guidance(sparql_query: str) -> Dict[str, Any]:
    """Query guidance ontology using SPARQL."""
    try:
        logger.debug(f"Executing query: {sparql_query}")
        result = bfg9k.query_ontology(sparql_query)
        logger.debug(f"Query result: {result}")
        return {"result": result}
    except Exception as e:
        logger.error(f"Query error: {e}")
        return {"error": str(e)}

@app.post("/update_guidance", operation_id="update_guidance")
async def update_guidance(content: str) -> Dict[str, Any]:
    """Update guidance ontology."""
    try:
        logger.debug(f"Updating content: {content[:100]}...")
        with open("temp_update.ttl", "w") as f:
            f.write(content)
        result = bfg9k.update_ontology("temp_update.ttl")
        logger.debug(f"Update result: {result}")
        return {"result": result}
    except Exception as e:
        logger.error(f"Update error: {e}")
        return {"error": str(e)}

@app.get("/echo", operation_id="echo")
async def echo(text: str) -> Dict[str, Any]:
    """Echoes the input string."""
    return {"result": text}

# Initialize and mount MCP
mcp = FastApiMCP(app)
mcp.mount(app, mount_path="/mcp", transport="sse")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 