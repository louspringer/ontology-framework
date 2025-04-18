#!/usr/bin/env python3
"""Tests for GraphDB client."""

import pytest
from pathlib import Path
from typing import Dict, Any
from ontology_framework.graphdb_client import GraphDBClient, GraphDBError

def test_create_repository(test_monitor):
    """Test repository creation."""
    client = GraphDBClient()
    assert client.create_repository()
    
    # Check server logs for repository creation
    metrics = test_monitor.get_test_metrics()["test_create_repository"]
    assert any("Repository created" in log.get("message", "") 
              for log in metrics["server_logs"])
              
def test_import_data(test_monitor, tmp_path):
    """Test data import."""
    client = GraphDBClient()
    
    # Create test data
    test_file = tmp_path / "test.ttl"
    test_file.write_text("""
        @prefix ex: <http://example.org/> .
        ex:Test a ex:TestClass .
    """)
    
    assert client.import_data(test_file)
    
    # Check server logs for import
    metrics = test_monitor.get_test_metrics()["test_import_data"]
    assert any("Data imported" in log.get("message", "") 
              for log in metrics["server_logs"])
              
def test_query(test_monitor):
    """Test SPARQL query."""
    client = GraphDBClient()
    
    result = client.query("""
        SELECT ?s ?p ?o
        WHERE {
            ?s ?p ?o
        }
        LIMIT 1
    """)
    
    assert result is not None
    
    # Check server logs for query execution
    metrics = test_monitor.get_test_metrics()["test_query"]
    assert any("Query executed" in log.get("message", "") 
              for log in metrics["server_logs"])
              
def test_error_handling(test_monitor):
    """Test error handling."""
    client = GraphDBClient()
    
    with pytest.raises(GraphDBError) as exc_info:
        client.query("INVALID SPARQL")
        
    error = exc_info.value
    assert error.correlation_id is not None
    assert error.status_code is not None
    
    # Check server logs for error
    metrics = test_monitor.get_test_metrics()["test_error_handling"]
    assert any("Error" in log.get("message", "") 
              for log in metrics["server_logs"])
              
def test_slow_query(test_monitor):
    """Test slow query detection."""
    client = GraphDBClient()
    
    # This query should be slow enough to trigger monitoring
    result = client.query("""
        SELECT ?s ?p ?o
        WHERE {
            ?s ?p ?o
        }
    """)
    
    assert result is not None
    
    # Check if test was marked as slow
    slow_tests = test_monitor.get_slow_tests(threshold=0.1)  # 100ms threshold
    assert "test_slow_query" in [t["test_name"] for t in slow_tests] 