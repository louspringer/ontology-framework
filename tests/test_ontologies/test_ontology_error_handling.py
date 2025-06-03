"""Tests for ontology error handling."""

import pytest
from rdflib import Graph, Namespace, RDF, RDFS, Literal, XSD
from pyshacl import validate
from pathlib import Path
from ontology_framework.modules.error_handling import ErrorHandler, ErrorType, ValidationRule

ERROR = Namespace("http://example.org/guidance# ")

def test_error_ontology_loads():
    """Test that the error handling ontology can be loaded."""
    g = Graph()
    ontology_path = Path("src/ontology_framework/ontologies/error_handling.ttl")
    assert ontology_path.exists(), "Error handling ontology file not found"
    g.parse(ontology_path,
        format="turtle")
    assert len(g) > 0, "Error handling ontology is empty"

def test_error_ontology_validation():
    """Test error handling ontology validation."""
    g = Graph()
    ontology_path = Path("src/ontology_framework/ontologies/error_handling.ttl")
    g.parse(ontology_path, format="turtle")
    
    # Validate against SHACL shapes
    shapes_graph = Graph()
    shapes_path = Path("src/ontology_framework/ontologies/error_handling_shapes.ttl")
    shapes_graph.parse(shapes_path, format="turtle")
    
    validation_result = validate(g,
        shacl_graph=shapes_graph)
    conforms, results_graph, results_text = validation_result
    
    assert conforms, f"Error handling ontology validation failed:\n{results_text}"

def test_error_types_defined():
    """Test that all error types are defined in the ontology."""
    g = Graph()
    ontology_path = Path("src/ontology_framework/ontologies/error_handling.ttl")
    g.parse(ontology_path, format="turtle")
    
    # Check that all error types from ErrorType enum are defined
    for error_type in ErrorType:
        error_uri = ERROR[error_type.value]
        assert (error_uri, RDF.type, ERROR.ErrorType) in g, f"Error type {error_type.value} not defined in ontology"

def test_validation_rules_defined():
    """Test that all validation rules are defined in the ontology."""
    g = Graph()
    ontology_path = Path("src/ontology_framework/ontologies/error_handling.ttl")
    g.parse(ontology_path, format="turtle")
    
    # Check that all validation rules from ValidationRule enum are defined
    for rule in ValidationRule:
        rule_uri = ERROR[rule.value]
        assert (rule_uri, RDF.type, ERROR.ValidationRule) in g, f"Validation rule {rule.value} not defined in ontology"
