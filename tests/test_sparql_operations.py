#!/usr/bin/env python3
"""Tests for SPARQL operations module."""

import pytest
from datetime import datetime
from ontology_framework.sparql_operations import (
    execute_sparql,
    QueryType,
    QueryResult,
    Neo4jExecutor,
    GraphDBExecutor,
    SparqlExecutor
)
import unittest
from unittest.mock import MagicMock, patch

class MockResponse:
    """Mock response for requests."""
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        
    def json(self):
        return self.json_data
        
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP Error {self.status_code}")

@pytest.fixture
def mock_requests(monkeypatch):
    """Mock requests module."""
    def mock_get(*args, **kwargs):
        return MockResponse({})
        
    def mock_post(*args, **kwargs):
        if "sparql" in args[0]:
            return MockResponse({
                "results": {
                    "bindings": [
                        {"s": {"type": "uri", "value": "http://example.org/test"}}
                    ]
                }
            })
        elif "update" in args[0]:
            return MockResponse({})
            
    monkeypatch.setattr("requests.get", mock_get)
    monkeypatch.setattr("requests.post", mock_post)

def test_query_result_str():
    """Test QueryResult string representation."""
    result = QueryResult(
        success=True,
        data=[{"test": "data"}],
        error=None,
        execution_time=1.23,
        query_type=QueryType.SELECT,
        timestamp=datetime.now(),
        query="SELECT ?s WHERE { ?s ?p ?o }",
        empty=False
    )
    
    assert "SUCCESS" in str(result)
    assert "SELECT" in str(result)
    assert "1.23" in str(result)
    
    result.empty = True
    assert "EMPTY" in str(result)
    
    result.success = False
    assert "FAILURE" in str(result)

def test_execute_select_query(mock_requests):
    """Test executing a SELECT query."""
    result = execute_sparql("SELECT ?s WHERE { ?s ?p ?o }")
    
    assert result.success
    assert not result.empty
    assert result.query_type == QueryType.SELECT
    assert len(result.data) == 1
    assert result.data[0]["s"]["value"] == "http://example.org/test"

def test_execute_ask_query(mock_requests):
    """Test executing an ASK query."""
    def mock_post(*args, **kwargs):
        return MockResponse({"boolean": True})
        
    import requests
    requests.post = mock_post
    
    result = execute_sparql("ASK { ?s ?p ?o }", query_type=QueryType.ASK)
    
    assert result.success
    assert not result.empty
    assert result.query_type == QueryType.ASK
    assert result.data is True

def test_execute_update_query(mock_requests):
    """Test executing an UPDATE query."""
    result = execute_sparql(
        "INSERT DATA { <http://example.org/test> <http://example.org/p> <http://example.org/o> }",
        query_type=QueryType.INSERT
    )
    
    assert result.success
    assert not result.empty
    assert result.query_type == QueryType.INSERT
    assert result.data is True

def test_empty_results(mock_requests):
    """Test handling of empty results."""
    def mock_post(*args, **kwargs):
        return MockResponse({"results": {"bindings": []}})
        
    import requests
    requests.post = mock_post
    
    result = execute_sparql("SELECT ?s WHERE { ?s ?p ?o }")
    
    assert result.success
    assert result.empty
    assert len(result.data) == 0

def test_error_handling(mock_requests):
    """Test error handling."""
    def mock_post(*args, **kwargs):
        return MockResponse({}, status_code=500)
        
    import requests
    requests.post = mock_post
    
    result = execute_sparql("SELECT ?s WHERE { ?s ?p ?o }")
    
    assert not result.success
    assert result.empty
    assert result.error is not None

def test_neo4j_executor():
    """Test Neo4j executor placeholder."""
    executor = Neo4jExecutor()
    
    with pytest.raises(NotImplementedError):
        executor.execute_query("SELECT ?s WHERE { ?s ?p ?o }", QueryType.SELECT)

def test_custom_endpoint(mock_requests):
    """Test using a custom endpoint."""
    executor = GraphDBExecutor(endpoint="http://custom-endpoint:7200", repository="test")
    result = execute_sparql("SELECT ?s WHERE { ?s ?p ?o }", executor=executor)
    
    assert result.success
    assert not result.empty 

class TestGraphDBExecutor(unittest.TestCase):
    """Test cases for GraphDBExecutor."""
    
    def setUp(self):
        """Set up test environment."""
        self.endpoint = "http://localhost:7200"
        self.repository = "test_repo"
        self.executor = GraphDBExecutor(self.endpoint, self.repository)
        
    def test_execute_query(self):
        """Test query execution."""
        test_query = "SELECT * WHERE { ?s ?p ?o }"
        test_results = {
            "results": {
                "bindings": [
                    {"s": {"value": "http://example.org/subject"},
                     "p": {"value": "http://example.org/predicate"},
                     "o": {"value": "http://example.org/object"}}
                ]
            }
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = test_results
            results = self.executor.execute_query(test_query)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["s"], "http://example.org/subject")
            
    def test_error_handling(self):
        """Test error handling."""
        test_query = "INVALID QUERY"
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.text = "Invalid query syntax"
            with self.assertRaises(Exception):
                self.executor.execute_query(test_query)
                
class TestNeo4jExecutor(unittest.TestCase):
    """Test cases for Neo4jExecutor."""
    
    def setUp(self):
        """Set up test environment."""
        self.endpoint = "bolt://localhost:7687"
        self.executor = Neo4jExecutor(self.endpoint)
        
    def test_execute_query(self):
        """Test query execution."""
        test_query = "MATCH (n) RETURN n"
        test_results = [{"n": {"value": "test"}}]
        
        with patch('neo4j.GraphDatabase.driver') as mock_driver:
            mock_session = MagicMock()
            mock_session.run.return_value = test_results
            mock_driver.return_value.session.return_value = mock_session
            
            results = self.executor.execute_query(test_query)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["n"], {"value": "test"})
            
    def test_error_handling(self):
        """Test error handling."""
        test_query = "INVALID QUERY"
        
        with patch('neo4j.GraphDatabase.driver') as mock_driver:
            mock_session = MagicMock()
            mock_session.run.side_effect = Exception("Invalid query")
            mock_driver.return_value.session.return_value = mock_session
            
            with self.assertRaises(Exception):
                self.executor.execute_query(test_query)
                
if __name__ == '__main__':
    unittest.main() 