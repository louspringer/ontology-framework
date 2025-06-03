"""Tests for the implementation dependency analyzer."""

import pytest
from pathlib import Path
import networkx as nx
from src.ontology_framework.modules.implementation_dependency_analyzer import ImplementationDependencyAnalyzer


@pytest.fixture
def sample_src():
    return Path("src/ontology_framework")


@pytest.fixture
def analyzer(sample_src):
    return ImplementationDependencyAnalyzer(sample_src)


def test_analyzer_initialization(analyzer):
    """Test analyzer initialization."""
    assert analyzer.src_path is not None
    assert analyzer.dependency_graph is not None
    assert analyzer.module_cache == {}
    assert analyzer.class_cache == {}


def test_module_dependencies(analyzer):
    """Test module dependency analysis."""
    deps = analyzer.analyze_module_dependencies()
    assert isinstance(deps, dict)
    assert all(isinstance(v, set) for v in deps.values())
    # Check for expected module dependencies
    assert "ontology_framework.modules" in deps
    assert "rdflib" in deps["ontology_framework.modules"]


def test_class_dependencies(analyzer):
    """Test class dependency analysis."""
    deps = analyzer.analyze_class_dependencies()
    assert isinstance(deps, dict)
    assert all(isinstance(v, set) for v in deps.values())
    # Check for expected class dependencies
    assert "OntologyDependencyAnalyzer" in deps
    assert "ImplementationDependencyAnalyzer" in deps


def test_method_dependencies(analyzer):
    """Test method dependency analysis."""
    deps = analyzer.analyze_method_dependencies()
    assert isinstance(deps, dict)
    assert all(isinstance(v, set) for v in deps.values())
    # Check for expected method dependencies
    assert "OntologyDependencyAnalyzer.build_dependency_graph" in deps
    assert "ImplementationDependencyAnalyzer.build_dependency_graph" in deps


def test_build_dependency_graph(analyzer):
    """Test complete dependency graph construction."""
    graph = analyzer.build_dependency_graph()
    assert isinstance(graph, nx.DiGraph)
    assert len(graph.nodes()) > 0
    assert len(graph.edges()) > 0
    # Check for expected edge types
    edge_types = {data['type'] for _, _, data in graph.edges(data=True)}
    assert {'module', 'class', 'method'}.issubset(edge_types)


def test_module_name_conversion(analyzer):
    """Test module name conversion."""
    test_path = Path("src/ontology_framework/modules/test.py")
    module_name = analyzer._get_module_name(test_path)
    assert module_name == "ontology_framework.modules.test" 