import os
import tempfile
from pathlib import Path
from scripts.namespace_dependency_analyzer import NamespaceDependencyAnalyzer

def test_parse_inventory() -> None:
    """Test parsing of inventory file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""
# Example.org Usage Inventory

## test.ttl
@prefix ex: <http://example.org/test#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

ex:Test a rdf:Class .

## test.py
from rdflib import Namespace
EX = Namespace("http://example.org/test#")
        """)
        f.flush()
        
        analyzer = NamespaceDependencyAnalyzer(f.name)
        analyzer.parse_inventory()
        
        assert len(analyzer.dependencies) == 2
        assert "test.ttl" in analyzer.dependencies
        assert "test.py" in analyzer.dependencies
        assert len(analyzer.graph.nodes) > 0
        assert len(analyzer.namespace_usage) > 0
        assert len(analyzer.errors) == 0
        
        os.unlink(f.name)

def test_validate_uri() -> None:
    """Test URI validation."""
    analyzer = NamespaceDependencyAnalyzer()
    
    # Valid URIs
    assert analyzer.validate_uri("http://example.org/test#")
    assert analyzer.validate_uri("http://example.org/")
    
    # Invalid URIs
    assert not analyzer.validate_uri("http:/example.org/test#")
    assert not analyzer.validate_uri("example.org/test#")
    
    assert len(analyzer.errors) == 2

def test_malformed_uris() -> None:
    """Test handling of malformed URIs."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""
# Example.org Usage Inventory

## test.ttl
@prefix ex: <http:/example.org/test#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

ex:Test a rdf:Class .

## test.py
from rdflib import Namespace
EX = Namespace("http:/example.org/test#")
        """)
        f.flush()
        
        analyzer = NamespaceDependencyAnalyzer(f.name)
        analyzer.parse_inventory()
        
        assert len(analyzer.errors) == 2
        assert "http:/example.org/test#" in str(analyzer.errors)
        assert len(analyzer.dependencies) == 0  # No valid URIs should be processed
        
        os.unlink(f.name)

def test_generate_analysis_report() -> None:
    """Test generation of analysis report."""
    analyzer = NamespaceDependencyAnalyzer()
    analyzer.dependencies = {
        "test.ttl": {"ex:http://example.org/test#"},
        "test.py": {"EX:http://example.org/test#"}
    }
    analyzer.namespace_usage = {
        "http://example.org/test#": {"definitions": 2, "references": 1}
    }
    
    report = analyzer.generate_analysis_report()
    assert "# Namespace Dependency Analysis Report" in report
    assert "## Summary Statistics" in report
    assert "## Namespace Usage Analysis" in report
    assert "## Dependency Analysis" in report
    assert "http://example.org/test#" in report

def test_save_analysis_report() -> None:
    """Test saving analysis report to file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        analyzer = NamespaceDependencyAnalyzer()
        analyzer.dependencies = {
            "test.ttl": {"ex:http://example.org/test#"}
        }
        analyzer.namespace_usage = {
            "http://example.org/test#": {"definitions": 1, "references": 0}
        }
        analyzer.save_analysis_report(f.name)
        
        with open(f.name, 'r') as report:
            content = report.read()
            assert "# Namespace Dependency Analysis Report" in content
            assert "http://example.org/test#" in content
            assert "WARNING: This namespace is defined but never referenced" in content
        
        os.unlink(f.name) 