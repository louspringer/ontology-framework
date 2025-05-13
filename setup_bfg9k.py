from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from pyshacl import validate
import os
import json

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
BFG9K = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
SH = Namespace("http://www.w3.org/ns/shacl#")

def setup_cursor_mcp():
    """Set up BFG9K as a Cursor IDE MCP service."""
    # Create Cursor MCP configuration
    mcp_config = {
        "name": "guidance-mcp",
        "version": "1.0.0",
        "description": "Guidance ontology MCP service for Cursor IDE",
        "entrypoint": "ontology_framework.mcp.guidance_mcp_service:GuidanceMCPService",
        "config": {
            "ontology_path": "guidance.ttl",
            "validation_enabled": True,
            "sse_enabled": True
        }
    }
    
    # Write MCP configuration
    os.makedirs(".cursor/mcp", exist_ok=True)
    with open(".cursor/mcp/guidance-mcp.json", "w") as f:
        json.dump(mcp_config, f, indent=2)

def update_governing_models():
    # Load guidance ontology
    g = Graph()
    g.parse("guidance.ttl", format="turtle")
    
    # Add BFG9K governance rules
    governance_rules = [
        (BFG9K.SemanticFirst, "Semantic First Approach", "Always use semantic web tools before text-based operations"),
        (BFG9K.ValidationApproach, "Validation Approach", "How to handle validation tasks"),
        (BFG9K.OntologyManagement, "Ontology Management", "Rules for managing ontologies")
    ]
    
    for rule, label, comment in governance_rules:
        g.add((rule, RDF.type, BFG9K.GovernanceRule))
        g.add((rule, RDFS.label, Literal(label)))
        g.add((rule, RDFS.comment, Literal(comment)))
    
    # Add SHACL shapes for governance
    shapes_graph = Graph()
    
    # GovernanceRule shape
    governance_shape = BFG9K.GovernanceRuleShape
    shapes_graph.add((governance_shape, RDF.type, SH.NodeShape))
    shapes_graph.add((governance_shape, SH.targetClass, BFG9K.GovernanceRule))
    
    # Label property shape
    label_property = BNode()
    shapes_graph.add((governance_shape, SH.property, label_property))
    shapes_graph.add((label_property, SH.path, RDFS.label))
    shapes_graph.add((label_property, SH.minCount, Literal(1)))
    shapes_graph.add((label_property, SH.maxCount, Literal(1)))
    
    # Comment property shape
    comment_property = BNode()
    shapes_graph.add((governance_shape, SH.property, comment_property))
    shapes_graph.add((comment_property, SH.path, RDFS.comment))
    shapes_graph.add((comment_property, SH.minCount, Literal(1)))
    shapes_graph.add((comment_property, SH.maxCount, Literal(1)))
    
    # Validate and merge
    conforms, results_graph, results_text = validate(
        g,
        shacl_graph=shapes_graph,
        ont_graph=None,
        inference='rdfs',
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        meta_shacl=False,
        debug=False,
        js=False
    )
    
    if not conforms:
        print("Validation failed:")
        print(results_text)
        return
    
    g += shapes_graph
    g.serialize("guidance.ttl", format="turtle")

def verify_setup():
    """Verify the BFG9K MCP setup."""
    print("\nVerifying BFG9K MCP setup...")
    
    # Check MCP configuration
    if not os.path.exists(".cursor/mcp/guidance-mcp.json"):
        print("❌ MCP configuration not found")
        return False
    
    print("✅ MCP configuration found")
    
    # Check MCP service
    try:
        import subprocess
        result = subprocess.run(["cursor", "mcp", "list"], capture_output=True, text=True)
        if "guidance-mcp" not in result.stdout:
            print("❌ BFG9K MCP service not found")
            return False
    except Exception as e:
        print(f"❌ Failed to check MCP service: {e}")
        return False
    
    print("✅ BFG9K MCP service found")
    print("\nSetup verification complete!")
    return True

def main():
    print("Setting up Cursor IDE MCP service...")
    setup_cursor_mcp()
    
    print("Updating governing models...")
    update_governing_models()
    
    print("Installation complete. The Guidance MCP service will be available in Cursor IDE.")
    print("To verify the setup:")
    print("1. Restart Cursor IDE")
    print("2. Check the MCP services list in Cursor settings")
    print("3. The guidance-mcp service should be listed and active")

if __name__ == "__main__":
    main() 