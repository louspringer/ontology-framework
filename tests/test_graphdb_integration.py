#!/usr/bin/env python3
"""Integration tests for GraphDB client."""

import os
import time
import json
import pytest
from pathlib import Path
from typing import Generator, Dict, Any, List
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
from pyshacl import validate
import requests

from ontology_framework.graphdb_client import GraphDBClient, GraphDBError

# Define test namespaces
TEST = Namespace("http://example.org/test#")
GDB = Namespace("http://example.org/graphdb#")
REQ = Namespace("http://example.org/requirement#")
RISK = Namespace("http://example.org/risk#")
CONST = Namespace("http://example.org/constraint#")

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

@pytest.fixture
def graphdb_client() -> Generator[GraphDBClient, None, None]:
    """Create a GraphDB client for testing."""
    client = GraphDBClient(
        base_url="http://localhost:7200",
        repository="test"
    )
    
    # Wait for server to be ready
    max_retries = 10
    retry_delay = 2
    for _ in range(max_retries):
        try:
            if client.check_server_status():
                break
        except GraphDBError:
            time.sleep(retry_delay)
    else:
        pytest.skip("GraphDB server is not running")
    
    yield client

@pytest.fixture
def test_repository(graphdb_client: GraphDBClient) -> Generator[str, None, None]:
    """Create a test repository."""
    repository_id = f"test_{int(time.time())}"
    
    # Create repository
    assert graphdb_client.create_repository(repository_id, "Test Repository")
    
    # Wait for repository to be ready
    max_retries = 10
    retry_delay = 2
    for _ in range(max_retries):
        try:
            if repository_id in [repo["id"] for repo in graphdb_client.list_repositories()]:
                break
        except GraphDBError:
            time.sleep(retry_delay)
    else:
        pytest.fail("Failed to create test repository")
    
    yield repository_id
    
    # Cleanup
    try:
        graphdb_client.delete_repository(repository_id)
    except GraphDBError:
        pass

def test_server_status(graphdb_client: GraphDBClient):
    """Test server status check."""
    assert graphdb_client.check_server_status()

def test_repository_management(graphdb_client: GraphDBClient, test_repository: str):
    """Test repository management operations."""
    # List repositories
    repositories = graphdb_client.list_repositories()
    assert isinstance(repositories, list)
    assert any(repo["id"] == test_repository for repo in repositories)
    
    # Delete repository
    assert graphdb_client.delete_repository(test_repository)
    
    # Verify repository is deleted
    repositories = graphdb_client.list_repositories()
    assert not any(repo["id"] == test_repository for repo in repositories)

def test_repository_data_management(graphdb_client: GraphDBClient, test_repository: str):
    """Test data management operations."""
    # Create test data
    g = Graph()
    g.add((URIRef("http://example.org/test#Test1"), RDF.type, OWL.Class))
    g.add((URIRef("http://example.org/test#Test1"), RDFS.label, Literal("Test Class")))
    
    # Upload data
    assert graphdb_client.upload_graph(g)
    
    # Verify data
    result = graphdb_client.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
    assert len(result["results"]["bindings"]) == 2
    
    # Clear data
    assert graphdb_client.clear_graph()
    
    # Verify data is cleared
    result = graphdb_client.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
    assert len(result["results"]["bindings"]) == 0

def test_repository_sparql_query(graphdb_client: GraphDBClient, test_repository: str):
    """Test SPARQL query operations."""
    # Create test data
    g = Graph()
    g.add((URIRef("http://example.org/test#Test1"), RDF.type, OWL.Class))
    g.add((URIRef("http://example.org/test#Test1"), RDFS.label, Literal("Test Class")))
    assert graphdb_client.upload_graph(g)
    
    # Test SELECT query
    result = graphdb_client.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
    assert len(result["results"]["bindings"]) == 2
    
    # Test CONSTRUCT query
    result = graphdb_client.query("CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }", format="turtle")
    assert isinstance(result, str)
    assert "Test Class" in result

def test_repository_sparql_update(graphdb_client: GraphDBClient, test_repository: str):
    """Test SPARQL update operations."""
    # Test INSERT DATA
    update = """
    INSERT DATA {
        <http://example.org/test#Test1> a owl:Class ;
            rdfs:label "Test Class" .
    }
    """
    assert graphdb_client.update(update)
    
    # Verify data
    result = graphdb_client.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
    assert len(result["results"]["bindings"]) == 2
    
    # Test DELETE DATA
    update = """
    DELETE DATA {
        <http://example.org/test#Test1> a owl:Class ;
            rdfs:label "Test Class" .
    }
    """
    assert graphdb_client.update(update)
    
    # Verify data is deleted
    result = graphdb_client.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
    assert len(result["results"]["bindings"]) == 0

def test_repository_validation(graphdb_client: GraphDBClient, test_repository: str):
    """Test SHACL validation."""
    # Upload shapes
    g = Graph()
    g.parse(data=TEST_SHAPES, format="turtle")
    assert graphdb_client.upload_graph(g, graph_uri="http://example.org/shapes")
    
    # Upload test data
    g = Graph()
    g.add((URIRef("http://example.org/test#Test1"), RDF.type, URIRef("http://example.org/test#TestClass")))
    g.add((URIRef("http://example.org/test#Test1"), URIRef("http://example.org/test#hasValue"), Literal("test")))
    assert graphdb_client.upload_graph(g)
    
    # Run validation
    result = graphdb_client.query("""
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX test: <http://example.org/test#>
    
    SELECT ?focusNode ?resultPath ?resultMessage
    WHERE {
        ?report a sh:ValidationReport ;
            sh:result ?result .
        ?result sh:focusNode ?focusNode ;
            sh:resultPath ?resultPath ;
            sh:resultMessage ?resultMessage .
    }
    """)
    assert len(result["results"]["bindings"]) == 0  # No validation errors 