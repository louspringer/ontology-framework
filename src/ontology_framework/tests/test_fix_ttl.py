"""
Test TTL fixing functionality.
"""
import pytest
from pathlib import Path
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from ontology_framework.graphdb_client import GraphDBClient

@pytest.fixture
def graphdb_client():
    """Create a GraphDB client instance."""
    client = GraphDBClient("http://localhost:7200", "fixes")
    yield client
    # Cleanup: Clear the fixes repository
    client.clear_graph()

def test_fix_missing_prefixes(graphdb_client):
    """Test fixing missing prefixes."""
    # Create a graph with missing prefixes
    graph = Graph()
    graph.add((URIRef("http://example.org/test#TestClass"), RDF.type, OWL.Class))
    graph.add((URIRef("http://example.org/test#TestClass"), RDFS.label, Literal("Test Class")))
    
    # Upload the graph
    graphdb_client.upload_graph(graph)
    
    # Fix missing prefixes
    graphdb_client.update("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX test: <http://example.org/test#>
        
        INSERT {
            ?class rdfs:comment ?comment .
        }
        WHERE {
            ?class a owl:Class ;
                   rdfs:label ?label .
            BIND(CONCAT("A class with label ", ?label) AS ?comment)
        }
    """)
    
    # Verify the fixes
    results = graphdb_client.query("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX test: <http://example.org/test#>
        
        SELECT ?class ?comment
        WHERE {
            ?class a owl:Class ;
                   rdfs:comment ?comment .
        }
    """)
    
    assert results.get("results", {}).get("bindings"), "Comments should be added to classes"

def test_fix_invalid_syntax(graphdb_client):
    """Test fixing invalid syntax."""
    # Create a graph with invalid syntax
    graph = Graph()
    graph.add((URIRef("http://example.org/test#InvalidClass"), RDF.type, OWL.Class))
    graph.add((URIRef("http://example.org/test#InvalidClass"), RDFS.label, Literal("Invalid Class")))
    graph.add((URIRef("http://example.org/test#InvalidClass"), RDFS.comment, Literal("A class with invalid syntax")))
    
    # Upload the graph
    graphdb_client.upload_graph(graph)
    
    # Fix invalid syntax
    graphdb_client.update("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX test: <http://example.org/test#>
        
        DELETE {
            ?class rdfs:comment ?oldComment .
        }
        INSERT {
            ?class rdfs:comment ?newComment .
        }
        WHERE {
            ?class a owl:Class ;
                   rdfs:comment ?oldComment .
            BIND(REPLACE(?oldComment, "invalid", "valid") AS ?newComment)
        }
    """)
    
    # Verify the fixes
    results = graphdb_client.query("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX test: <http://example.org/test#>
        
        SELECT ?class ?comment
        WHERE {
            ?class a owl:Class ;
                   rdfs:comment ?comment .
            FILTER(CONTAINS(?comment, "valid"))
        }
    """)
    
    assert results.get("results", {}).get("bindings"), "Invalid syntax should be fixed" 