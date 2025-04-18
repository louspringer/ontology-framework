#!/usr/bin/env python3
"""Tests for GraphDB-based patch management."""

import pytest
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from ontology_framework.patch_management import GraphDBPatchManager, PatchNotFoundError

# Test data
TEST_PATCH = """
@prefix : <./test#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix patch: <http://example.org/patch#> .

:TestPatch a patch:Patch ;
    rdfs:label "Test Patch" ;
    rdfs:comment "A test patch for validation" ;
    patch:hasOperation [
        a patch:AddOperation ;
        patch:hasSubject :TestSubject ;
        patch:hasPredicate rdfs:label ;
        patch:hasObject "Test Object" ;
    ] .
"""

@pytest.fixture
def patch_manager():
    """Create a test patch manager."""
    manager = GraphDBPatchManager(repository="test-ontology-framework")
    yield manager
    # Cleanup after tests
    manager.client.session.close()

def test_load_ontology(patch_manager):
    """Test loading an ontology into GraphDB."""
    # Create test ontology
    test_file = Path("test_ontology.ttl")
    test_file.write_text(TEST_PATCH)
    
    try:
        # Load ontology
        assert patch_manager.load_ontology(test_file)
        
        # Verify data was loaded
        query = """
        SELECT ?s ?p ?o
        WHERE {
            ?s ?p ?o
        }
        LIMIT 1
        """
        results = patch_manager.client.query(query)
        assert results is not None
        assert len(results) > 0
        
    finally:
        # Cleanup
        test_file.unlink()

def test_load_dependencies(patch_manager):
    """Test loading ontology dependencies."""
    # Create test directory with ontologies
    test_dir = Path("test_ontologies")
    test_dir.mkdir(exist_ok=True)
    
    try:
        # Create test ontologies
        (test_dir / "ontology1.ttl").write_text(TEST_PATCH)
        (test_dir / "ontology2.ttl").write_text(TEST_PATCH)
        
        # Load dependencies
        assert patch_manager.load_dependencies(test_dir)
        
        # Verify data was loaded
        query = """
        SELECT (COUNT(*) as ?count)
        WHERE {
            ?s ?p ?o
        }
        """
        results = patch_manager.client.query(query)
        assert results is not None
        assert int(results[0]["count"]) > 0
        
    finally:
        # Cleanup
        for file in test_dir.glob("*.ttl"):
            file.unlink()
        test_dir.rmdir()

def test_apply_patch(patch_manager):
    """Test applying a patch."""
    # Load test patch
    test_file = Path("test_patch.ttl")
    test_file.write_text(TEST_PATCH)
    
    try:
        # Load patch
        assert patch_manager.load_ontology(test_file)
        
        # Apply patch
        patch_uri = URIRef("http://example.org/test#TestPatch")
        assert patch_manager.apply_patch(patch_uri)
        
        # Verify patch was applied
        query = """
        SELECT ?o
        WHERE {
            :TestSubject rdfs:label ?o
        }
        """
        results = patch_manager.client.query(query)
        assert results is not None
        assert len(results) > 0
        assert results[0]["o"] == "Test Object"
        
    finally:
        # Cleanup
        test_file.unlink()

def test_get_change_history(patch_manager):
    """Test retrieving change history."""
    # Load test patch
    test_file = Path("test_patch.ttl")
    test_file.write_text(TEST_PATCH)
    
    try:
        # Load patch
        assert patch_manager.load_ontology(test_file)
        
        # Get change history
        history = patch_manager.get_change_history()
        assert isinstance(history, list)
        assert len(history) > 0
        
        # Verify change record structure
        record = history[0]
        assert "change" in record
        assert "operation" in record
        assert "timestamp" in record
        assert "details" in record
        
    finally:
        # Cleanup
        test_file.unlink()

def test_patch_not_found(patch_manager):
    """Test handling of non-existent patch."""
    with pytest.raises(PatchNotFoundError):
        patch_manager.load_patch("nonexistent-patch") 