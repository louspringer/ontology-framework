import os
import tempfile
from pathlib import Path
from scripts.namespace_dependency_mapper import NamespaceDependencyMapper

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
        
        mapper = NamespaceDependencyMapper(f.name)
        mapper.parse_inventory()
        
        assert len(mapper.dependencies) == 2
        assert "test.ttl" in mapper.dependencies
        assert "test.py" in mapper.dependencies
        assert len(mapper.graph.nodes) > 0
        
        os.unlink(f.name)

def test_generate_migration_plan() -> None:
    """Test generation of migration plan."""
    mapper = NamespaceDependencyMapper()
    mapper.dependencies = {
        "test.ttl": {"ex:http://example.org/test#"},
        "test.py": {"EX:http://example.org/test#"},
        "test.md": {"ex:http://example.org/test#"}
    }
    
    plan = mapper.generate_migration_plan()
    assert "# Namespace Migration Plan" in plan
    assert "### 1. Ontology Namespaces" in plan
    assert "### 2. Python Namespaces" in plan
    assert "### 3. Documentation References" in plan
    assert "https://ontologies.louspringer.com/test/" in plan

def test_save_migration_plan() -> None:
    """Test saving migration plan to file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        mapper = NamespaceDependencyMapper()
        mapper.dependencies = {
            "test.ttl": {"ex:http://example.org/test#"}
        }
        mapper.save_migration_plan(f.name)
        
        with open(f.name, 'r') as plan:
            content = plan.read()
            assert "# Namespace Migration Plan" in content
            assert "https://ontologies.louspringer.com/test/" in content
        
        os.unlink(f.name) 