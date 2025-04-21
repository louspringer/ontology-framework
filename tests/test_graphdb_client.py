#!/usr/bin/env python3
"""Tests for the GraphDB client."""

from pathlib import Path
from typing import Generator

import pytest
import tempfile

from ontology_framework.graphdb_client import GraphDBClient, GraphDBError
from tests.utils.mock_graphdb import MockGraphDBServer
from tests.utils.test_monitoring import TestMonitor

@pytest.fixture
def graphdb_client(mock_graphdb_server: MockGraphDBServer) -> GraphDBClient:
    """Create a GraphDB client for testing."""
    return GraphDBClient(
        endpoint=mock_graphdb_server.url,
        repository="test_repo",
        username="test_user",
        password="test_pass"
    )

def test_create_repository(test_monitor: TestMonitor) -> None:
    """Test repository creation."""
    client = GraphDBClient(endpoint="http://localhost:7200", repository="test_repo")
    with test_monitor.monitor_test("test_create_repository"):
        client.create_repository("test_repo")
        assert test_monitor.check_logs_for_message("Repository 'test_repo' created")

def test_import_data(test_monitor: TestMonitor) -> None:
    """Test data import."""
    client = GraphDBClient(endpoint="http://localhost:7200", repository="test_repo")
    with test_monitor.monitor_test("test_import_data"):
        with tempfile.NamedTemporaryFile(suffix=".ttl") as temp_file:
            temp_file.write(b"@prefix ex: <http://example.org/> .\nex:test a ex:Test .")
            temp_file.flush()
            client.import_data(temp_file.name)
            assert test_monitor.check_logs_for_message(f"Data imported from {temp_file.name}")

def test_query(test_monitor: TestMonitor) -> None:
    """Test query execution."""
    client = GraphDBClient(endpoint="http://localhost:7200", repository="test_repo")
    with test_monitor.monitor_test("test_query"):
        result = client.query("SELECT * WHERE { ?s ?p ?o }")
        assert result is not None
        assert test_monitor.check_logs_for_message("Query executed")

def test_error_handling(test_monitor: TestMonitor) -> None:
    """Test error handling."""
    client = GraphDBClient(endpoint="http://localhost:7200", repository="test_repo")
    with test_monitor.monitor_test("test_error_handling"):
        with pytest.raises(GraphDBError):
            client.query("INVALID SPARQL")
        assert test_monitor.check_logs_for_error("Error executing query")

def test_slow_query(test_monitor: TestMonitor) -> None:
    """Test slow query detection."""
    client = GraphDBClient(endpoint="http://localhost:7200", repository="test_repo")
    with test_monitor.monitor_test("test_slow_query"):
        # This query should be slow enough to trigger the warning
        client.query("SELECT * WHERE { ?s ?p ?o } OFFSET 1000000")
        assert test_monitor.check_logs_for_slow_query("Slow query detected")