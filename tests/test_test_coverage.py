"""Tests for test coverage analysis."""

import pytest
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from src.ontology_framework.modules.test_coverage import TestCoverageAnalyzer

# Define namespaces
TEST = Namespace("http://example.org/test# ")
IMPL = Namespace("http://example.org/implementation#")
GUIDANCE = Namespace("http://example.org/guidance#")


@pytest.fixture
def guidance_graph():
    """Create a test guidance graph with coverage requirements."""
    g = Graph()

    # Add test coverage requirement
    req = URIRef("http://example.org/guidance# TestCoverageReq")
    g.add((req, RDF.type, GUIDANCE.TestCoverageRequirement))

    coverage = URIRef("http://example.org/guidance# CoverageSpec")
    g.add((req, GUIDANCE.requiresCoverage, coverage))
    g.add((coverage, GUIDANCE.component, IMPL["TestComponent"]))
    g.add((coverage, GUIDANCE.coverageThreshold, Literal(80.0)))

    return g


@pytest.fixture
def test_component():
    """Create a test component with methods."""
    return {"TestComponent": {"method1", "method2", "method3"}}


@pytest.fixture
def test_coverage():
    """Create test coverage data."""
    return {
        "test_method1": {"TestComponent"},
        "test_method2": {"TestComponent"},
        "test_method3": {"OtherComponent"},
    }


def test_analyzer_initialization(guidance_graph):
    """Test analyzer initialization."""
    analyzer = TestCoverageAnalyzer(guidance_graph)
    assert analyzer.guidance == guidance_graph
    assert analyzer.src_path.exists()
    assert analyzer.test_path.exists()
    assert len(analyzer.coverage_graph) > 0


def test_analyze_source_files(guidance_graph, tmp_path):
    """Test source file analysis."""
    # Create a test source file
    src_dir = tmp_path / "src" / "ontology_framework" / "test_module"
    src_dir.mkdir(parents=True)
    test_file = src_dir / "test_component.py"
    test_file.write_text(
        """
class TestComponent:
    def method1(self):
        pass
        
    def method2(self):
        pass
        
    def method3(self):
        pass
"""
    )

    analyzer = TestCoverageAnalyzer(guidance_graph)
    analyzer.src_path = src_dir.parent
    components = analyzer.analyze_source_files()
    assert "test_module.test_component.TestComponent" in components
    assert components["test_module.test_component.TestComponent"] == {
        "method1",
        "method2",
        "method3",
    }


def test_analyze_test_files(guidance_graph, tmp_path):
    """Test test file analysis."""
    # Create a test file
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    test_file = test_dir / "test_component.py"
    test_file.write_text(
        """
from src.ontology_framework.test_module.test_component import TestComponent
def test_coverage_method1():
    pass
    
def test_method2():
    pass
"""
    )

    analyzer = TestCoverageAnalyzer(guidance_graph)
    analyzer.test_path = test_dir
    coverage = analyzer.analyze_test_files()
    assert "test_coverage_method1" in coverage
    assert "test_method2" in coverage
    assert (
        "src.ontology_framework.test_module.test_component.TestComponent"
        in coverage["test_coverage_method1"]
    )


def test_validate_coverage(guidance_graph, test_component, test_coverage):
    """Test coverage validation."""
    analyzer = TestCoverageAnalyzer(guidance_graph)

    # Mock the analysis methods
    analyzer.analyze_source_files = lambda: test_component
    analyzer.analyze_test_files = lambda: test_coverage
    coverage_graph = analyzer.validate_coverage()

    # Check component
    comp_uri = IMPL["TestComponent"]
    assert (comp_uri, RDF.type, IMPL.Component) in coverage_graph

    # Check methods
    for method in ["method1", "method2", "method3"]:
        method_uri = IMPL[f"TestComponent.{method}"]
        assert (method_uri, RDF.type, IMPL.Method) in coverage_graph
        assert (comp_uri, IMPL.hasMethod, method_uri) in coverage_graph

    # Check test coverage
    for test in ["test_coverage_method1", "test_method2"]:
        test_uri = TEST[test]
        assert (test_uri, RDF.type, TEST.TestCase) in coverage_graph
        assert (test_uri, TEST.dependsOn, comp_uri) in coverage_graph


def test_generate_report(guidance_graph, test_component, test_coverage):
    """Test report generation."""
    analyzer = TestCoverageAnalyzer(guidance_graph)

    # Mock the analysis methods
    analyzer.analyze_source_files = lambda: test_component
    analyzer.analyze_test_files = lambda: test_coverage

    # Generate coverage graph
    analyzer.validate_coverage()

    # Generate report
    report = analyzer.generate_report()

    # Check report content
    assert "Test Coverage Report" in report
    assert "Component: TestComponent" in report
    assert "Required Coverage: 80.0%" in report
    assert "Actual Coverage: 66.7%" in report  # 2/3 methods covered
    assert "Tests: 2" in report
    assert "Methods: 3" in report
    assert "Status: FAIL" in report  # Below 80% threshold
