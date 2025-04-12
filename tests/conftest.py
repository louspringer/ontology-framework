#!/usr/bin/env python3
"""
Pytest configuration for the ontology framework tests.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Configure logging for tests
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test fixtures
import pytest
from rdflib import Graph, Namespace

@pytest.fixture
def test_namespace():
    """Fixture providing a test namespace."""
    return Namespace("http://example.org/test#")

@pytest.fixture
def empty_graph():
    """Fixture providing an empty RDF graph."""
    return Graph()

@pytest.fixture
def valid_model_graph(test_namespace):
    """Fixture providing a valid model graph."""
    graph = Graph()
    graph.add((test_namespace.ValidClass, RDF.type, OWL.Class))
    graph.add((test_namespace.ValidClass, RDFS.label, Literal("Valid Class")))
    graph.add((test_namespace.ValidClass, RDFS.comment, Literal("A valid class")))
    graph.add((test_namespace.ValidClass, OWL.versionInfo, Literal("1.0.0")))
    return graph

@pytest.fixture
def temp_dir():
    """Fixture providing a temporary directory."""
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir) 