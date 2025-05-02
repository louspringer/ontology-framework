"""
Test stereo validation functionality.
"""
import pytest
from pathlib import Path
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from ontology_framework.graphdb_client import GraphDBClient

@pytest.fixture
def graphdb_client():
    """Create a GraphDB client instance."""
    client = GraphDBClient("http://localhost:7200", "stereo")
    yield client
    # Cleanup: Clear the stereo repository
    client.clear_graph()

def test_validate_stereo(graphdb_client):
    """Test stereo validation."""
    # Create a valid stereo graph
    graph = Graph()
    graph.add((URIRef("http://example.org/stereo#StereoClass"), RDF.type, OWL.Class))
    graph.add((URIRef("http://example.org/stereo#StereoClass"), RDFS.label, Literal("Stereo Class")))
    graph.add((URIRef("http://example.org/stereo#StereoClass"), RDFS.comment, Literal("A stereo class")))
    graph.add((URIRef("http://example.org/stereo#hasStereo"), RDF.type, OWL.ObjectProperty))
    graph.add((URIRef("http://example.org/stereo#hasStereo"), RDFS.domain, URIRef("http://example.org/stereo#StereoClass")))
    graph.add((URIRef("http://example.org/stereo#hasStereo"), RDFS.range, RDFS.Literal))
    
    # Upload the graph
    graphdb_client.upload_graph(graph)
    
    # Validate stereo properties
    results = graphdb_client.query("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX stereo: <http://example.org/stereo#>
        
        ASK {
            ?class a owl:Class ;
                   rdfs:label ?label ;
                   rdfs:comment ?comment .
            ?property a owl:ObjectProperty ;
                     rdfs:domain ?class ;
                     rdfs:range rdfs:Literal .
        }
    """)
    
    assert results.get("boolean", False), "Stereo validation should pass"

def test_validate_invalid_stereo(graphdb_client):
    """Test stereo validation with invalid data."""
    # Create an invalid stereo graph
    graph = Graph()
    graph.add((URIRef("http://example.org/stereo#InvalidClass"), RDF.type, OWL.Class))
    graph.add((URIRef("http://example.org/stereo#InvalidClass"), RDFS.label, Literal("Invalid Class")))
    graph.add((URIRef("http://example.org/stereo#hasInvalid"), RDF.type, OWL.ObjectProperty))
    graph.add((URIRef("http://example.org/stereo#hasInvalid"), RDFS.domain, URIRef("http://example.org/stereo#InvalidClass")))
    # Missing range declaration
    
    # Upload the graph
    graphdb_client.upload_graph(graph)
    
    # Validate stereo properties
    results = graphdb_client.query("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX stereo: <http://example.org/stereo#>
        
        ASK {
            ?class a owl:Class ;
                   rdfs:label ?label .
            ?property a owl:ObjectProperty ;
                     rdfs:domain ?class .
            FILTER NOT EXISTS { ?property rdfs:range ?range }
        }
    """)
    
    assert results.get("boolean", False), "Stereo validation should detect missing range" 