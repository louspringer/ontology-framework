#!/usr/bin/env python3
"""Tests for the GraphDB client."""

import os
import tempfile
from pathlib import Path
from typing import Generator
import pytest
import requests
from unittest.mock import patch, MagicMock, mock_open, Mock
from rdflib import Graph, Namespace, RDF, RDFS, OWL, SH, Literal
from rdflib.namespace import XSD
from pyshacl import validate
import logging

from ontology_framework.graphdb_client import GraphDBClient, GraphDBError
from ontology_framework.exceptions import GraphDBError as OntologyFrameworkError

# Define test namespaces
TEST = Namespace("http://example.org/test#")
EX = Namespace("http://example.org/")

# Define test shapes
TEST_SHAPES = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix test: <http://example.org/test#> .

test:TestShape a sh:NodeShape ;
    sh:targetClass test:TestClass ;
    sh:property [
        sh:path test:hasValue ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
    ] .
"""

logger = logging.getLogger(__name__)

@pytest.fixture
def test_graph() -> Graph:
    """Create a test graph with proper RDF structure."""
    g = Graph()
    g.bind('test', TEST)
    g.bind('ex', EX)
    g.bind('rdf', RDF)
    g.bind('rdfs', RDFS)
    g.bind('owl', OWL)
    
    # Add class definition
    g.add((TEST.TestClass, RDF.type, OWL.Class))
    g.add((TEST.TestClass, RDFS.label, Literal("Test Class")))
    
    # Add instance
    g.add((TEST.TestInstance, RDF.type, TEST.TestClass))
    g.add((TEST.TestInstance, TEST.hasValue, Literal("test value")))
    
    return g

@pytest.fixture
def test_shapes() -> Graph:
    """Create a test shapes graph."""
    g = Graph()
    g.parse(data=TEST_SHAPES, format='turtle')
    return g

@pytest.fixture
def graphdb_client():
    """Create a GraphDB client instance."""
    return GraphDBClient("http://localhost:7200", "test")

@pytest.fixture
def mock_response():
    """Create a mock response object."""
    response = MagicMock()
    response.status_code = 204
    return response

def validate_graph(g: Graph, shapes: Graph) -> bool:
    """Validate a graph against SHACL shapes."""
    conforms, _, _ = validate(g, shacl_graph=shapes)
    return conforms

def test_query(graphdb_client: GraphDBClient, test_graph: Graph):
    """Test executing a SPARQL query."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": {
            "bindings": [
                {"s": {"value": str(TEST.TestInstance)}},
                {"p": {"value": str(TEST.hasValue)}},
                {"o": {"value": "test value", "type": "literal"}}
            ]
        }
    }
    with patch('requests.post', return_value=mock_response):
        result = graphdb_client.query("SELECT * WHERE { ?s ?p ?o }")
        assert result["results"]["bindings"][0]["s"]["value"] == str(TEST.TestInstance)

def test_update(graphdb_client: GraphDBClient, mock_response):
    """Test executing a SPARQL update."""
    with patch('requests.post', return_value=mock_response):
        result = graphdb_client.update("INSERT DATA { <s> <p> <o> }")
        assert result is True

def test_upload_graph(graphdb_client: GraphDBClient, mock_response, test_graph: Graph, test_shapes: Graph):
    """Test uploading a graph."""
    # Validate test graph before upload
    assert validate_graph(test_graph, test_shapes)
    
    with patch('requests.post', return_value=mock_response):
        result = graphdb_client.upload_graph(test_graph)
        assert result is True

def test_download_graph(graphdb_client: GraphDBClient, test_graph: Graph, test_shapes: Graph):
    """Test downloading a graph."""
    mock_response = MagicMock()
    mock_response.text = test_graph.serialize(format='turtle')
    
    with patch('requests.get', return_value=mock_response):
        result = graphdb_client.download_graph()
        assert isinstance(result, Graph)
        assert len(result) == len(test_graph)
        assert validate_graph(result, test_shapes)

def test_clear_graph(graphdb_client: GraphDBClient, mock_response):
    """Test clearing a graph."""
    with patch('requests.delete', return_value=mock_response):
        result = graphdb_client.clear_graph()
        assert result is True

def test_list_graphs(graphdb_client: GraphDBClient):
    """Test listing graphs."""
    mock_response = MagicMock()
    mock_response.json.return_value = [{"graphName": "graph1"}, {"graphName": "graph2"}]
    with patch('requests.get', return_value=mock_response):
        result = graphdb_client.list_graphs()
        assert result == ["graph1", "graph2"]

def test_count_triples(graphdb_client: GraphDBClient):
    """Test counting triples."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": {
            "bindings": [
                {"count": {"value": "42"}}
            ]
        }
    }
    with patch('requests.post', return_value=mock_response):
        result = graphdb_client.count_triples()
        assert result == 42

def test_get_graph_info(graphdb_client: GraphDBClient):
    """Test getting graph info."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": {
            "bindings": [
                {"count": {"value": "42"}}
            ]
        }
    }
    with patch('requests.post', return_value=mock_response):
        result = graphdb_client.get_graph_info()
        assert result["triples"] == 42
        assert result["uri"] == "default"

def test_backup_graph(graphdb_client: GraphDBClient, mock_response, test_graph: Graph, test_shapes: Graph):
    """Test backing up a graph."""
    mock_response.text = test_graph.serialize(format='turtle')
    
    with patch('requests.get', return_value=mock_response):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ttl') as temp_file:
            result = graphdb_client.backup_graph(temp_file.name)
            assert result is True
            assert os.path.exists(temp_file.name)
            
            # Verify the backed up graph
            backup_graph = Graph()
            backup_graph.parse(temp_file.name, format='turtle')
            assert validate_graph(backup_graph, test_shapes)
            assert len(backup_graph) == len(test_graph)
            
            os.unlink(temp_file.name)

def test_restore_graph(graphdb_client: GraphDBClient, mock_response, test_graph: Graph, test_shapes: Graph):
    """Test restoring a graph from backup."""
    with patch('requests.post', return_value=mock_response), \
         patch('requests.delete', return_value=mock_response):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ttl') as temp_file:
            # Save graph to file using RDFlib
            test_graph.serialize(destination=temp_file.name, format='turtle')
            temp_file.flush()
            
            result = graphdb_client.restore_graph(temp_file.name)
            assert result is True
            os.unlink(temp_file.name)

def test_load_ontology(graphdb_client: GraphDBClient, mock_response, test_graph: Graph, test_shapes: Graph):
    """Test loading an ontology."""
    with patch('requests.post', return_value=mock_response), \
         patch('requests.delete', return_value=mock_response), \
         patch('requests.get', return_value=mock_response), \
         tempfile.NamedTemporaryFile(delete=False, suffix='.ttl') as temp_file:
        # Save ontology to file using RDFlib
        test_graph.serialize(destination=temp_file.name, format='turtle')
        temp_file.flush()
        
        result = graphdb_client.load_ontology(temp_file.name)
        assert result is True
        os.unlink(temp_file.name)

def test_error_handling(graphdb_client: GraphDBClient):
    """Test error handling."""
    # Test server error response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    
    with patch('requests.post', return_value=mock_response):
        with pytest.raises(GraphDBError, match="Upload failed"):
            graphdb_client.upload_graph("test.ttl")
            
    # Test connection error
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError("Failed to connect")):
        with pytest.raises(GraphDBError, match="List graphs failed"):
            graphdb_client.list_graphs()
            
    # Test timeout error
    with patch('requests.delete', side_effect=requests.exceptions.Timeout("Request timed out")):
        with pytest.raises(GraphDBError, match="Clear failed"):
            graphdb_client.clear_graph()

def test_check_server_status(graphdb_client):
    """Test checking server status."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        assert graphdb_client.check_server_status() is True
        mock_get.assert_called_once_with("http://localhost:7200/rest/repositories")

def test_server_status_error(graphdb_client):
    """Test server status check with error."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Test error")
        assert graphdb_client.check_server_status() is False

def test_load_ontology_error(graphdb_client):
    """Test loading an ontology with error."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
        with pytest.raises(GraphDBError):
            graphdb_client.load_ontology(Path("test.ttl"))

def test_execute_sparql(graphdb_client):
    """Test executing SPARQL query."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"results": {"bindings": []}}
        results = graphdb_client.execute_sparql("SELECT * WHERE { ?s ?p ?o }")
        assert results["results"]["bindings"] == []
        mock_post.assert_called_once()

def test_execute_sparql_error(graphdb_client):
    """Test executing SPARQL query with error."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
        with pytest.raises(GraphDBError):
            graphdb_client.execute_sparql("SELECT * WHERE { ?s ?p ?o }")

def test_check_server_status_error(graphdb_client):
    """Test server status check with error."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Test error")
        assert graphdb_client.check_server_status() is False

def test_load_ontology_error(graphdb_client):
    """Test loading an ontology with error."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
        with pytest.raises(GraphDBError):
            graphdb_client.load_ontology(Path("test.ttl"))

def test_execute_sparql_error(graphdb_client):
    """Test executing SPARQL query with error."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()
        with pytest.raises(GraphDBError):
            graphdb_client.execute_sparql("SELECT * WHERE { ?s ?p ?o }")

class TestGraphDBClient:
    """Test suite for GraphDB client functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.endpoint = "http://localhost:7200"
        self.repository = "test-repo"
        self.client = GraphDBClient(self.endpoint, self.repository)
        
    def test_connection(self):
        """Test GraphDB connection"""
        logger.info("Testing GraphDB connection")
        try:
            self.client.dataset_exists(self.repository)
        except GraphDBError as e:
            pytest.skip(f"Failed to connect to GraphDB: {str(e)}")
            
    def test_dataset_operations(self):
        """Test dataset operations"""
        # Create dataset
        self.client.create_dataset(self.repository)
        assert self.client.dataset_exists(self.repository)
        
        # Load test data
        test_data = """
        @prefix ex: <http://example.org/> .
        ex:test a ex:TestClass ;
            ex:property "test value" .
        """
        self.client.load_ontology(self.repository, test_data)
        
        # Query test data
        query = """
        PREFIX ex: <http://example.org/>
        SELECT ?s ?p ?o
        WHERE {
            ?s ?p ?o .
        }
        """
        results = self.client.execute_query(query, self.repository)
        assert len(results) > 0
        
        # Clean up
        self.client.delete_dataset(self.repository)
        assert not self.client.dataset_exists(self.repository)
        
    def test_query_execution(self):
        """Test SPARQL query execution"""
        # Create test dataset
        self.client.create_dataset(self.repository)
        
        # Load test data
        test_data = """
        @prefix ex: <http://example.org/> .
        ex:test1 a ex:TestClass ;
            ex:property "value1" .
        ex:test2 a ex:TestClass ;
            ex:property "value2" .
        """
        self.client.load_ontology(self.repository, test_data)
        
        # Test SELECT query
        select_query = """
        PREFIX ex: <http://example.org/>
        SELECT ?s ?o
        WHERE {
            ?s ex:property ?o .
        }
        """
        results = self.client.execute_query(select_query, self.repository)
        assert len(results) == 2
        
        # Test CONSTRUCT query
        construct_query = """
        PREFIX ex: <http://example.org/>
        CONSTRUCT {
            ?s ex:newProperty ?o
        }
        WHERE {
            ?s ex:property ?o
        }
        """
        results = self.client.execute_query(construct_query, self.repository)
        assert len(results) > 0
        
        # Clean up
        self.client.delete_dataset(self.repository)
        
    def test_error_handling(self):
        """Test error handling"""
        # Test invalid endpoint
        with pytest.raises(GraphDBError):
            invalid_client = GraphDBClient("http://invalid:7200", "test")
            invalid_client.dataset_exists("test")
            
        # Test invalid query
        self.client.create_dataset(self.repository)
        with pytest.raises(GraphDBError):
            self.client.execute_query("INVALID SPARQL", self.repository)
        self.client.delete_dataset(self.repository)