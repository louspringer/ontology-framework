from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from bfg9k_manager import BFG9KManager

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
BFG9K = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
TOOL = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/tool#")

def register_tools():
    """Register tools with BFG9K"""
    manager = BFG9KManager()
    
    # Define tools
    tools = [
        {
            "uri": TOOL.GraphDBClient "label": "GraphDB Client",
            "comment": "Client for interacting with GraphDB repository",
            "type": "SemanticTool",
            "priority": "HIGH",
            "validation": True
        },
        {
            "uri": TOOL.RDFlib,
            "label": "RDFlib",
            "comment": "Python library for RDF graph manipulation",
            "type": "SemanticTool",
            "priority": "HIGH",
            "validation": True
        },
        {
            "uri": TOOL.PySHACL,
            "label": "PySHACL",
            "comment": "Python implementation of SHACL validation",
            "type": "ValidationTool",
            "priority": "HIGH",
            "validation": True
        },
        {
            "uri": TOOL.SPARQL,
            "label": "SPARQL",
            "comment": "Query language for RDF data",
            "type": "QueryTool",
            "priority": "HIGH",
            "validation": True
        },
        {
            "uri": TOOL.clpm,
            "label": "CLPM",
            "comment": "Configuration and package management tool",
            "type": "ManagementTool",
            "priority": "HIGH",
            "validation": True
        }
    ]
    
    # Register each tool
    for tool in tools:
        # Add tool definition
        update = f"""
        PREFIX tool: <{TOOL}>
        PREFIX bfg9k: <{BFG9K}>
        PREFIX rdfs: <{RDFS}>
        
        INSERT DATA {{
            <{tool['uri']}> a bfg9k:Tool ;
                           rdfs:label "{tool['label']}" ;
                           rdfs:comment "{tool['comment']}" ;
                           bfg9k:toolType "{tool['type']}" ;
                           bfg9k:priority "{tool['priority']}" ;
                           bfg9k:requiresValidation {str(tool['validation']).lower()} .
        }}
        """
        manager.query_ontology(update)
        
        # Add validation rule for the tool
        rule_uri = f"{tool['uri']}Rule"
        manager.add_governance_rule(
            rule_uri f"{tool['label']} Validation Rule",
            f"Validation rules for {tool['label']}"
        )

if __name__ == "__main__":
    register_tools() 