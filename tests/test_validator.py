#!/usr/bin/env python3
"""Test script to demonstrate Python validation."""

import pytest
from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
from src.ontology_framework.modules.validator import (
    MCPValidator,
    ValidationTarget
)
from ontology_framework.validation.python_validator import PythonValidator

# Define namespaces
BFG = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

@pytest.fixture
def test_ontology():
    """Create a test ontology graph."""
    g = Graph()
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("sh", SH)
    g.bind("bfg", BFG)
    
    # Add some test triples
    class_uri = URIRef("http://example.org/TestClass")
    prop_uri = URIRef("http://example.org/testProperty")
    instance_uri = URIRef("http://example.org/testInstance")
    
    g.add((class_uri, RDF.type, OWL.Class))
    g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
    g.add((instance_uri, RDF.type, class_uri))
    g.add((instance_uri, prop_uri, Literal("test value")))
    
    return g

@pytest.fixture
def validator():
    """Create a validator instance."""
    return MCPValidator()

def test_validation_target():
    """Test ValidationTarget class."""
    target = ValidationTarget(
        uri=URIRef("http://example.org/TestClass"),
        target_type="class",
        priority="HIGH"
    )
    assert str(target.uri) == "http://example.org/TestClass"
    assert target.target_type == "class"
    assert target.priority == "HIGH"
    assert not target.validation_errors
    
    target.add_error("Test error")
    assert "Test error" in target.validation_errors

def test_validator_initialization():
    """Test validator initialization."""
    validator = MCPValidator()
    assert isinstance(validator.config, dict)
    assert isinstance(validator.validation_rules, dict)
    assert "validate_bfg9k" in validator.validation_rules
    assert "validateHierarchy" in validator.validation_rules
    assert "validateSemantics" in validator.validation_rules
    assert "validateSHACL" in validator.validation_rules
    assert "validateProperties" in validator.validation_rules
    assert "validateIndividuals" in validator.validation_rules

def test_acquire_targets(validator, test_ontology):
    """Test target acquisition."""
    targets = validator.acquire_targets(test_ontology)
    assert isinstance(targets, dict)
    assert "classes" in targets
    assert "properties" in targets
    assert "shapes" in targets
    assert "individuals" in targets

def test_validate_target(validator, test_ontology):
    """Test target validation."""
    target = ValidationTarget(
        uri=URIRef("http://example.org/TestClass"),
        target_type="class"
    )
    errors = validator.validate_target(target, test_ontology)
    assert isinstance(errors, list)

def test_validate_hierarchy(validator, test_ontology):
    """Test hierarchy validation."""
    errors = validator.validate_hierarchy(test_ontology)
    assert isinstance(errors, list)

def test_validate_semantics(validator, test_ontology):
    """Test semantics validation."""
    errors = validator.validate_semantics(test_ontology)
    assert isinstance(errors, list)

def test_validate_shacl(validator, test_ontology):
    """Test SHACL validation."""
    errors = validator.validate_shacl(test_ontology)
    assert isinstance(errors, list)

def test_validate_bfg9k(validator, test_ontology):
    """Test BFG9K validation."""
    errors = validator.validate_bfg9k(test_ontology)
    assert isinstance(errors, list)

def test_validate_properties(validator, test_ontology):
    """Test property validation."""
    errors = validator.validate_properties(test_ontology)
    assert isinstance(errors, list)

def test_validate_individuals(validator, test_ontology):
    """Test individual validation."""
    errors = validator.validate_individuals(test_ontology)
    assert isinstance(errors, list)

def test_validate(validator, test_ontology):
    """Test complete validation."""
    target = ValidationTarget(
        uri=URIRef("http://example.org/TestClass"),
        target_type="class"
    )
    ordinance = {
        "rules": ["validate_hierarchy", "validate_semantics"],
        "priority": "HIGH"
    }
    result = validator.validate(test_ontology, target, ordinance)
    assert isinstance(result, dict)

def main():
    """Run validation on sample.py and display results."""
    validator = PythonValidator()
    results = validator.validate_file("tests/test_data/sample.py")
    
    print("\nValidation Results:")
    print("==================")
    
    if results['conforms']:
        print("✅ All validations passed!")
    else:
        print("❌ Found validation issues:")
        for violation in results['results']:
            print(f"- {violation['message']} (Severity: {violation['severity']})")

if __name__ == "__main__":
    main() 