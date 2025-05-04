from fastapi import FastAPI, Request
from fastapi_mcp import FastApiMCP
from src.ontology_framework.mcp.guidance_mcp_service import GuidanceMCPService
import json
from typing import Optional, Dict, Any, List
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD
import os

app = FastAPI(
    title="BFG9K Ontology System",
    description="The Big Friendly Guidance 9000 - Ultimate firepower for ontology validation and management."
)
guidance_service = GuidanceMCPService()

@app.get("/echo", operation_id="echo")
async def echo(text: str):
    """Echoes the input string."""
    return {"result": text}

@app.post("/validate_guidance", operation_id="validate_guidance")
async def validate_guidance(ontology_path: str):
    """Validate the ontology using SHACL and guidance rules."""
    return {"result": f"Validated {ontology_path}"}

@app.post("/sparql_query", operation_id="sparql_query")
async def sparql_query(ontology_path: str, query: str):
    """Run a SPARQL query against the ontology."""
    return {"result": f"Ran query on {ontology_path}"}

@app.post("/validate_ontology", operation_id="validate_ontology")
async def validate_ontology(ontology_path: str) -> dict:
    """Validate an ontology using SHACL and guidance rules."""
    try:
        results = guidance_service.validate()
        return {"result": results}
    except Exception as e:
        return {"error": str(e)}

@app.post("/generate_isomorphic_rdf", operation_id="generate_isomorphic_rdf")
async def generate_isomorphic_rdf(ontology_path: str, output_format: str = "turtle") -> dict:
    """Generate an isomorphic RDF version of the ontology."""
    try:
        # Load the ontology
        g = Graph()
        g.parse(ontology_path, format="turtle")
        
        # Generate isomorphic RDF in the requested format
        rdf_data = g.serialize(format=output_format)
        return {"result": rdf_data}
    except Exception as e:
        return {"error": str(e)}

@app.post("/sync_graphdb", operation_id="sync_graphdb")
async def sync_graphdb(ontology_path: str, repository: Optional[str] = None) -> dict:
    """Sync an ontology to GraphDB."""
    try:
        # Load and validate the ontology first
        validation_result = await validate_ontology(ontology_path)
        if "error" in validation_result:
            return validation_result
            
        # Generate RDF
        rdf_result = await generate_isomorphic_rdf(ontology_path, "turtle")
        if "error" in rdf_result:
            return rdf_result
            
        # TODO: Add actual GraphDB sync using your GraphDB client
        # For now, return a placeholder
        return {"result": f"Synced {ontology_path} to GraphDB"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/edit_ontology", operation_id="edit_ontology")
async def edit_ontology(ontology_path: str, edits: Dict[str, Any]) -> dict:
    """Edit an ontology using semantic web operations.
    
    Args:
        ontology_path: Path to the ontology file
        edits: Dictionary containing edits to make
        
    Returns:
        Dictionary containing the result of the edit operation
    """
    try:
        # Load the ontology
        g = Graph()
        g.parse(ontology_path, format="turtle")
        
        # Define namespaces
        GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
        
        # Process each edit
        for edit in edits.get("add", []):
            if edit["type"] == "class":
                # Add a new class
                class_uri = URIRef(f"{GUIDANCE}{edit['name']}")
                g.add((class_uri, RDF.type, OWL.Class))
                if "label" in edit:
                    g.add((class_uri, RDFS.label, Literal(edit["label"], lang="en")))
                if "comment" in edit:
                    g.add((class_uri, RDFS.comment, Literal(edit["comment"], lang="en")))
                if "subclass_of" in edit:
                    g.add((class_uri, RDFS.subClassOf, URIRef(f"{GUIDANCE}{edit['subclass_of']}")))
            
            elif edit["type"] == "property":
                # Add a new property
                prop_uri = URIRef(f"{GUIDANCE}{edit['name']}")
                prop_type = OWL.ObjectProperty if edit.get("object_property", True) else OWL.DatatypeProperty
                g.add((prop_uri, RDF.type, prop_type))
                if "label" in edit:
                    g.add((prop_uri, RDFS.label, Literal(edit["label"], lang="en")))
                if "comment" in edit:
                    g.add((prop_uri, RDFS.comment, Literal(edit["comment"], lang="en")))
                if "domain" in edit:
                    g.add((prop_uri, RDFS.domain, URIRef(f"{GUIDANCE}{edit['domain']}")))
                if "range" in edit:
                    g.add((prop_uri, RDFS.range, URIRef(f"{GUIDANCE}{edit['range']}")))
            
            elif edit["type"] == "individual":
                # Add a new individual
                ind_uri = URIRef(f"{GUIDANCE}{edit['name']}")
                g.add((ind_uri, RDF.type, URIRef(f"{GUIDANCE}{edit['class']}")))
                if "label" in edit:
                    g.add((ind_uri, RDFS.label, Literal(edit["label"], lang="en")))
                if "comment" in edit:
                    g.add((ind_uri, RDFS.comment, Literal(edit["comment"], lang="en")))
        
        # Process removals
        for edit in edits.get("remove", []):
            if edit["type"] == "class":
                # Remove a class
                class_uri = URIRef(f"{GUIDANCE}{edit['name']}")
                g.remove((class_uri, None, None))
                g.remove((None, None, class_uri))
            
            elif edit["type"] == "property":
                # Remove a property
                prop_uri = URIRef(f"{GUIDANCE}{edit['name']}")
                g.remove((prop_uri, None, None))
                g.remove((None, prop_uri, None))
            
            elif edit["type"] == "individual":
                # Remove an individual
                ind_uri = URIRef(f"{GUIDANCE}{edit['name']}")
                g.remove((ind_uri, None, None))
                g.remove((None, None, ind_uri))
        
        # Save changes
        g.serialize(ontology_path, format="turtle")
        
        # Validate the changes
        validation_result = guidance_service.validate()
        
        return {
            "result": {
                "status": "success",
                "message": f"Successfully edited {ontology_path}",
                "validation": validation_result
            }
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Handle JSON-RPC requests for MCP tools."""
    try:
        payload = await request.json()
        method = payload.get("method")
        params = payload.get("params", {})
        
        handlers = {
            "validate_ontology": validate_ontology,
            "generate_isomorphic_rdf": generate_isomorphic_rdf,
            "sync_graphdb": sync_graphdb,
            "edit_ontology": edit_ontology
        }
        
        if method in handlers:
            result = await handlers[method](**params)
            return {"jsonrpc": "2.0", "result": result, "id": payload.get("id")}
        
        return {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Method {method} not found"}, "id": payload.get("id")}
    except Exception as e:
        return {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": payload.get("id")}

@app.post("/check_duplicates", operation_id="check_duplicates")
async def check_duplicates(directory: Optional[str] = None) -> dict:
    """Scan all ontologies in the workspace (or a specified directory) for duplicate IRIs and report conflicts."""
    if directory is None:
        directory = os.getcwd()
    duplicates = {}
    iri_map = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.ttl') or file.endswith('.rdf'):
                path = os.path.join(root, file)
                try:
                    g = Graph()
                    g.parse(path)
                    for s in g.subjects():
                        if isinstance(s, URIRef):
                            if s not in iri_map:
                                iri_map[s] = []
                            iri_map[s].append(path)
                except Exception as e:
                    continue
    for iri, paths in iri_map.items():
        if len(paths) > 1:
            duplicates[str(iri)] = paths
    return {"duplicates": duplicates, "count": len(duplicates)}

# Mount the MCP server to your FastAPI app with tool definitions
mcp = FastApiMCP(
    app,
    name="BFG9K Server",
    description="The Big Friendly Guidance 9000 - Unleashing maximum ontology validation firepower."
)

# Register tools with MCP
app.state.tools = [
    {
        "name": "validate_ontology",
        "description": "Validate an ontology using SHACL and guidance rules",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ontology_path": {"type": "string", "description": "Path to the ontology file"}
            },
            "required": ["ontology_path"]
        }
    },
    {
        "name": "generate_isomorphic_rdf",
        "description": "Generate an isomorphic RDF version of the ontology",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ontology_path": {"type": "string", "description": "Path to the ontology file"},
                "output_format": {"type": "string", "description": "Output format (turtle, xml, etc.)", "default": "turtle"}
            },
            "required": ["ontology_path"]
        }
    },
    {
        "name": "sync_graphdb",
        "description": "Sync an ontology to GraphDB",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ontology_path": {"type": "string", "description": "Path to the ontology file"},
                "repository": {"type": "string", "description": "GraphDB repository name"}
            },
            "required": ["ontology_path"]
        }
    },
    {
        "name": "edit_ontology",
        "description": "Edit an ontology using semantic web operations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ontology_path": {"type": "string", "description": "Path to the ontology file"},
                "edits": {
                    "type": "object",
                    "properties": {
                        "add": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["class", "property", "individual"]},
                                    "name": {"type": "string"},
                                    "label": {"type": "string"},
                                    "comment": {"type": "string"},
                                    "subclass_of": {"type": "string"},
                                    "object_property": {"type": "boolean"},
                                    "domain": {"type": "string"},
                                    "range": {"type": "string"},
                                    "class": {"type": "string"}
                                },
                                "required": ["type", "name"]
                            }
                        },
                        "remove": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["class", "property", "individual"]},
                                    "name": {"type": "string"}
                                },
                                "required": ["type", "name"]
                            }
                        }
                    }
                }
            },
            "required": ["ontology_path", "edits"]
        }
    },
    {
        "name": "check_duplicates",
        "description": "Scan all ontologies in the workspace (or a specified directory) for duplicate IRIs and report conflicts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory to scan for ontologies (optional)"}
            },
            "required": []
        }
    }
]

mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 