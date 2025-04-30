#!/usr/bin/env python3
"""Test suite for ontology dependency analyzer."""

from typing import Dict, List, Any
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from src.ontology_framework.modules.ontology_dependency_analyzer import OntologyDependencyAnalyzer
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
import networkx as nx

@pytest.fixture
def sample_ontology():
    return Path("tests/fixtures/sample_ontology.ttl")

@pytest.fixture
def analyzer(sample_ontology):
    return OntologyDependencyAnalyzer(sample_ontology)

def test_analyzer_initialization(analyzer):
    """Test analyzer initialization."""
    assert analyzer.ontology_path is not None
    assert analyzer.graph is not None
    assert analyzer.dependency_graph is not None

def test_namespace_dependencies(analyzer):
    """Test namespace dependency analysis."""
    deps = analyzer.analyze_namespace_dependencies()
    assert isinstance(deps, dict)
    assert all(isinstance(v, set) for v in deps.values())
    # Check for expected namespace dependencies
    assert "http://example.org/ontology#" in deps
    assert "http://example.org/test#" in deps

def test_class_dependencies(analyzer):
    """Test class dependency analysis."""
    deps = analyzer.analyze_class_dependencies()
    assert isinstance(deps, dict)
    assert all(isinstance(v, set) for v in deps.values())
    # Check for expected class hierarchies
    assert "TestClass" in deps
    assert "BaseClass" in deps

def test_property_dependencies(analyzer):
    """Test property dependency analysis."""
    deps = analyzer.analyze_property_dependencies()
    assert isinstance(deps, dict)
    assert all(isinstance(v, set) for v in deps.values())
    # Check for expected property relationships
    assert "hasProperty" in deps
    assert "TestClass" in deps["hasProperty"]

def test_constraint_dependencies(analyzer):
    """Test constraint dependency analysis."""
    deps = analyzer.analyze_constraint_dependencies()
    assert isinstance(deps, dict)
    assert all(isinstance(v, set) for v in deps.values())
    # Check for expected constraint relationships
    assert "TestConstraint" in deps
    assert "TestClass" in deps["TestConstraint"]

def test_build_dependency_graph(analyzer):
    """Test complete dependency graph construction."""
    graph = analyzer.build_dependency_graph()
    assert isinstance(graph, nx.DiGraph)
    assert len(graph.nodes()) > 0
    assert len(graph.edges()) > 0
    # Check for expected edge types
    edge_types = {data['type'] for _, _, data in graph.edges(data=True)}
    assert {'namespace', 'class', 'property', 'constraint'}.issubset(edge_types) 