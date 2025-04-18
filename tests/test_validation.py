#!/usr/bin/env python3
"""Tests for ontology validation."""

import pytest
import logging
from pathlib import Path
from src.ontology_framework.validation import OntologyValidator, ValidationError

@pytest.fixture
def validator():
    """Create a validator instance."""
    return OntologyValidator()

@pytest.fixture
def test_ontology_dir(tmp_path):
    """Create test ontology files."""
    # Valid ontology
    valid_onto = tmp_path / "valid.ttl"
    valid_onto.write_text("""
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    
    <http://example.org/ontology> a owl:Ontology .
    
    <http://example.org/Class1> a owl:Class ;
        rdfs:label "Class 1" ;
        rdfs:comment "Description of Class 1" .
    """)
    
    # Invalid Turtle syntax
    invalid_syntax = tmp_path / "invalid_syntax.ttl"
    invalid_syntax.write_text("""
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    
    <http://example.org/ontology> a owl:Ontology
    """)  # Missing period
    
    # Missing metadata
    missing_metadata = tmp_path / "missing_metadata.ttl"
    missing_metadata.write_text("""
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    
    <http://example.org/Class1> a owl:Class .
    """)
    
    return tmp_path

def test_validate_turtle_syntax(validator, test_ontology_dir, caplog):
    """Test Turtle syntax validation."""
    caplog.set_level(logging.INFO)
    
    # Test valid file
    valid_file = test_ontology_dir / "valid.ttl"
    errors = validator.validate_turtle_syntax(valid_file)
    assert not errors
    assert f"Validating Turtle syntax for {valid_file}" in caplog.text
    assert f"Successfully parsed {valid_file}" in caplog.text
    
    # Test invalid syntax
    invalid_file = test_ontology_dir / "invalid_syntax.ttl"
    errors = validator.validate_turtle_syntax(invalid_file)
    assert errors
    assert f"Turtle syntax error in {invalid_file}" in caplog.text
    
    # Test non-existent file
    with pytest.raises(ValidationError):
        validator.validate_turtle_syntax(test_ontology_dir / "nonexistent.ttl")

def test_validate_context_uri(validator, caplog):
    """Test context URI validation."""
    caplog.set_level(logging.INFO)
    
    # Test valid URI
    valid_uri = "http://example.org/ontology"
    errors = validator.validate_context_uri(valid_uri)
    assert not errors
    assert f"Validating context URI: {valid_uri}" in caplog.text
    assert f"Context URI {valid_uri} is valid" in caplog.text
    
    # Test file URI
    file_uri = "file:///path/to/file"
    errors = validator.validate_context_uri(file_uri)
    assert errors
    assert f"File URIs are not allowed for contexts: {file_uri}" in caplog.text
    
    # Test URI without scheme
    no_scheme = "example.org/ontology"
    errors = validator.validate_context_uri(no_scheme)
    assert errors
    assert f"URI {no_scheme} must have a scheme" in caplog.text

def test_validate_ontology_structure(validator, test_ontology_dir, caplog):
    """Test ontology structure validation."""
    caplog.set_level(logging.INFO)
    
    # Test valid ontology
    valid_file = test_ontology_dir / "valid.ttl"
    errors = validator.validate_ontology_structure(valid_file)
    assert not errors
    assert f"Validating ontology structure for {valid_file}" in caplog.text
    assert "Found 1 ontology declarations" in caplog.text
    assert "Found 1 classes" in caplog.text
    assert "Ontology structure validation passed" in caplog.text
    
    # Test missing metadata
    missing_file = test_ontology_dir / "missing_metadata.ttl"
    errors = validator.validate_ontology_structure(missing_file)
    assert errors
    assert "No owl:Ontology declaration found" in caplog.text
    assert "Class missing rdfs:label" in caplog.text
    assert "Class missing rdfs:comment" in caplog.text

def test_validate_before_import(validator, test_ontology_dir, caplog):
    """Test complete validation before import."""
    caplog.set_level(logging.INFO)
    
    # Test valid import
    valid_file = test_ontology_dir / "valid.ttl"
    valid_context = "http://example.org/ontology"
    errors = validator.validate_before_import(valid_file, valid_context)
    assert not errors
    assert "Starting pre-import validation" in caplog.text
    assert "All validations passed" in caplog.text
    
    # Test invalid import
    invalid_file = test_ontology_dir / "invalid_syntax.ttl"
    invalid_context = "file:///path/to/file"
    errors = validator.validate_before_import(invalid_file, invalid_context)
    assert errors
    assert "Validation failed" in caplog.text
    assert len(errors) >= 2  # Should have both syntax and context errors 