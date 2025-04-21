"""
Tests for the JenaFusekiClient class.
"""

import pytest
from unittest.mock import Mock, patch
import requests
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL

from ontology_framework.jena_client import (
    JenaFusekiClient,
    JenaError,
    JenaConnectionError,
    JenaQueryError,
    JenaUpdateError
)

@pytest.fixture
def client():
    """Create a JenaFusekiClient instance for testing."""
    return JenaFusekiClient("http://localhost:3030", "test_dataset")

@pytest.fixture
def sample_graph():
    """Create a sample RDF graph for testing."""
    g = Graph()
    ex = Namespace("http://example.org/")
    
    # Add some test triples
    g.add((ex.subject1, RDF.type, ex.Class1))
    g.add((ex.subject1, RDFS.label, Literal("Test Subject 1")))
    g.add((ex.subject1, ex.property1, ex.object1))
    
    return g

def test_init():
    """Test client initialization."""
    client = JenaFusekiClient("http://localhost:3030/", "test_dataset")
    assert client.endpoint_url == "http://localhost:3030"
    assert client.dataset == "test_dataset"
    assert client.query_url == "http://localhost:3030/test_dataset/query"
    assert client.update_url == "http://localhost:3030/test_dataset/update"
    assert client.graph_store_url == "http://localhost:3030/test_dataset/data"

@patch('requests.post')
def test_query_success(mock_post, client):
    """Test successful SPARQL query."""
    mock_response = Mock()
    mock_response.json.return_value = {
        'results': {
            'bindings': [
                {
                    'subject': {'value': 'http://example.org/subject1'},
                    'predicate': {'value': 'http://example.org/property1'},
                    'object': {'value': 'http://example.org/object1'}
                }
            ]
        }
    }
    mock_post.return_value = mock_response
    
    results = client.query("SELECT * WHERE { ?s ?p ?o }")
    
    assert len(results) == 1
    assert results[0]['subject'] == 'http://example.org/subject1'
    assert results[0]['predicate'] == 'http://example.org/property1'
    assert results[0]['object'] == 'http://example.org/object1'

@patch('requests.post')
def test_query_connection_error(mock_post, client):
    """Test query with connection error."""
    mock_post.side_effect = requests.ConnectionError("Connection failed")
    
    with pytest.raises(JenaConnectionError):
        client.query("SELECT * WHERE { ?s ?p ?o }")

@patch('requests.post')
def test_update_success(mock_post, client):
    """Test successful SPARQL update."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    client.update("INSERT DATA { <http://example.org/s> <http://example.org/p> <http://example.org/o> }")
    
    mock_post.assert_called_once()

@patch('requests.post')
def test_update_error(mock_post, client):
    """Test update with error."""
    mock_post.side_effect = requests.HTTPError("Update failed")
    
    with pytest.raises(JenaUpdateError):
        client.update("INVALID UPDATE")

@patch('requests.post')
def test_upload_graph_success(mock_post, client, sample_graph):
    """Test successful graph upload."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    client.upload_graph(sample_graph, "http://example.org/graph1")
    
    mock_post.assert_called_once()
    assert mock_post.call_args[1]['headers']['Content-Type'] == 'text/turtle'

@patch('requests.get')
def test_download_graph_success(mock_get, client):
    """Test successful graph download."""
    mock_response = Mock()
    mock_response.text = """
    @prefix ex: <http://example.org/> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    
    ex:subject1 rdf:type ex:Class1 .
    """
    mock_get.return_value = mock_response
    
    graph = client.download_graph("http://example.org/graph1")
    
    assert isinstance(graph, Graph)
    assert len(graph) > 0

@patch('requests.post')
def test_clear_graph_success(mock_post, client):
    """Test successful graph clear."""
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    client.clear_graph("http://example.org/graph1")
    
    mock_post.assert_called_once()

@patch('requests.post')
def test_list_graphs_success(mock_post, client):
    """Test successful graph listing."""
    mock_response = Mock()
    mock_response.json.return_value = {
        'results': {
            'bindings': [
                {'g': {'value': 'http://example.org/graph1'}},
                {'g': {'value': 'http://example.org/graph2'}}
            ]
        }
    }
    mock_post.return_value = mock_response
    
    graphs = client.list_graphs()
    
    assert len(graphs) == 2
    assert 'http://example.org/graph1' in graphs
    assert 'http://example.org/graph2' in graphs

@patch('requests.post')
def test_count_triples_success(mock_post, client):
    """Test successful triple counting."""
    mock_response = Mock()
    mock_response.json.return_value = {
        'results': {
            'bindings': [
                {'count': {'value': '42'}}
            ]
        }
    }
    mock_post.return_value = mock_response
    
    count = client.count_triples("http://example.org/graph1")
    
    assert count == 42

def test_error_hierarchy():
    """Test error class hierarchy."""
    assert issubclass(JenaConnectionError, JenaError)
    assert issubclass(JenaQueryError, JenaError)
    assert issubclass(JenaUpdateError, JenaError) 