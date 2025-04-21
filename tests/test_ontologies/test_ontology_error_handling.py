"""Tests for ontology error handling."""

import pytest
from rdflib import Graph, Namespace, RDF, RDFS, Literal, XSD
from pyshacl import validate
from pathlib import Path
from ontology_framework.modules.error_handling import ErrorHandler, ErrorType, ValidationRule

ERROR = Namespace("http://example.org/guidance#")

def test_error_ontology_loads() -> None:
    """Test that the error handling ontology can be loaded."""
    g = Graph()
    ontology_path = Path("src/ontology_framework/ontologies/error_handling.ttl")
    assert ontology_path.exists(), "Error handling ontology file not found"
    g.parse(ontology_path, format="turtle")
    assert len(g) > 0, "Error handling ontology is empty"

def test_error_types_exist() -> None:
    """Test that all required error types are defined."""
    g = Graph()
    g.parse("src/ontology_framework/ontologies/error_handling.ttl", format="turtle")
    required_errors = {
        "APIError", "IOError", "RuntimeError", "ValidationError",
        "TestError", "SecurityError", "ComplianceError", "DataError"
    }
    errors = {str(s).split("#")[-1] for s in g.subjects(predicate=RDFS.subClassOf, object=ERROR.Error)}
    assert errors == required_errors, f"Missing error types: {required_errors - errors}"

def test_error_handling_steps() -> None:
    """Test that error handling steps are properly defined."""
    g = Graph()
    g.parse("src/ontology_framework/ontologies/error_handling.ttl", format="turtle")
    required_steps = {
        "ErrorIdentification": 1,
        "ErrorAnalysis": 2,
        "ErrorRecovery": 3,
        "ErrorPrevention": 4
    }
    for step, order in required_steps.items():
        step_uri = ERROR[step]
        assert any(
            int(o) == order
            for o in g.objects(step_uri, ERROR.stepOrder)
        ), f"Missing or incorrect step order for {step}"

def test_validation_rules() -> None:
    """Test that validation rules are properly defined."""
    g = Graph()
    g.parse("src/ontology_framework/ontologies/error_handling.ttl", format="turtle")
    required_rules = {
        "SensitiveDataValidation",
        "RiskValidation",
        "MatrixValidation",
        "ComplianceValidation"
    }
    rules = {str(s).split("#")[-1] for s in g.subjects(predicate=RDF.type, object=ERROR.ValidationRule)}
    assert rules == required_rules, f"Missing validation rules: {required_rules - rules}"

def test_shacl_validation() -> None:
    """Test that the ontology passes SHACL validation."""
    g = Graph()
    g.parse("src/ontology_framework/ontologies/error_handling.ttl", format="turtle")
    conforms, _, _ = validate(g)
    assert conforms, "Ontology fails SHACL validation" 