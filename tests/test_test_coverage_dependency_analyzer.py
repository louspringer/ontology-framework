"""Tests for the test coverage dependency analyzer."""

import pytest
from pathlib import Path
import networkx as nx
from src.ontology_framework.modules.test_coverage_dependency_analyzer import TestCoverageDependencyAnalyzer

@pytest.fixture
def sample_test():
    return Path("tests")

@pytest.fixture
def sample_src():
    return Path("src/ontology_framework")

@pytest.fixture
def analyzer(sample_test, sample_src):
    return TestCoverageDependencyAnalyzer(sample_test, sample_src)

def test_analyzer_initialization(analyzer):
    """Test analyzer initialization."""
    assert analyzer.test_path is not None
    assert analyzer.src_path is not None
    assert analyzer.dependency_graph is not None
    assert analyzer.imports == {}
    assert analyzer.class_cache == {}

def test_test_imports(analyzer):
    """Test test import analysis."""
    imports = analyzer.analyze_test_imports()
    assert isinstance(imports, dict)
    assert all(isinstance(v, set) for v in imports.values())
    # Check for expected test imports
    assert "test_ontology_dependency_analyzer" in imports
    assert "src.ontology_framework.modules" in imports["test_ontology_dependency_analyzer"]

def test_test_targets(analyzer):
    """Test test target analysis."""
    targets = analyzer.analyze_test_targets()
    assert isinstance(targets, dict)
    assert all(isinstance(v, set) for v in targets.values())
    # Check for expected test targets
    assert "test_analyzer_initialization" in targets
    assert "OntologyDependencyAnalyzer" in targets["test_analyzer_initialization"]

def test_test_assertions(analyzer):
    """Test test assertion analysis."""
    assertions = analyzer.analyze_test_assertions()
    assert isinstance(assertions, dict)
    assert all(isinstance(v, set) for v in assertions.values())
    # Check for expected test assertions
    assert "test_analyzer_initialization" in assertions
    assert "assert" in str(assertions["test_analyzer_initialization"])

def test_build_dependency_graph(analyzer):
    """Test complete dependency graph construction."""
    graph = analyzer.build_dependency_graph()
    assert isinstance(graph, nx.DiGraph)
    assert len(graph.nodes()) > 0
    assert len(graph.edges()) > 0
    # Check for expected edge types
    edge_types = {data['type'] for _, _, data in graph.edges(data=True)}
    assert {'import', 'target', 'assertion'}.issubset(edge_types)
