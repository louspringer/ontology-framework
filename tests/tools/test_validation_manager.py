import os
import pytest
from pathlib import Path
from ontology_framework.tools.validation_manager import ValidationManager

@pytest.fixture
def temp_ontology_path(tmp_path):
    """Create a temporary ontology file for testing."""
    ontology_content = """
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix ont: <http://example.org/ontology#> .

    ont:ValidationRule a owl:Class ;
        rdfs:label "Validation Rule"@en ;
        rdfs:comment "A class representing validation rules"@en .

    ont:hasValue a owl:DatatypeProperty ;
        rdfs:domain ont:ValidationRule ;
        rdfs:range xsd:string ;
        rdfs:label "has value"@en ;
        rdfs:comment "The value associated with a validation rule"@en .
    """
    temp_file = tmp_path / "test_validation_rules.ttl"
    temp_file.write_text(ontology_content)
    return str(temp_file)

@pytest.fixture
def validation_manager(temp_ontology_path):
    """Create a ValidationManager instance with a temporary ontology."""
    return ValidationManager(temp_ontology_path)

def test_init_with_path(temp_ontology_path):
    """Test initialization with a specific ontology path."""
    manager = ValidationManager(temp_ontology_path)
    assert manager.graph is not None
    assert len(manager.graph) > 0

def test_init_with_default_path():
    """Test initialization without a specific path."""
    manager = ValidationManager()
    assert manager.graph is not None
    # The default ontology should have some triples
    assert len(manager.graph) > 0

def test_init_with_nonexistent_path():
    """Test initialization with a nonexistent path."""
    with pytest.raises(FileNotFoundError):
        ValidationManager("/nonexistent/path/to/ontology.ttl")

def test_add_validation_rule(validation_manager):
    """Test adding a new validation rule."""
    validation_manager.add_validation_rule("TestRule", "test value")
    rules = validation_manager.get_validation_rules()
    assert len(rules) == 1
    assert rules[0]["rule"].endswith("TestRule")
    assert rules[0]["value"] == "test value"

def test_get_validation_rules_empty(validation_manager):
    """Test getting validation rules when none exist."""
    rules = validation_manager.get_validation_rules()
    assert len(rules) == 0

def test_get_multiple_validation_rules(validation_manager):
    """Test getting multiple validation rules."""
    test_rules = [
        ("Rule1", "value1"),
        ("Rule2", "value2"),
        ("Rule3", "value3")
    ]
    for rule_name, rule_value in test_rules:
        validation_manager.add_validation_rule(rule_name, rule_value)
    
    rules = validation_manager.get_validation_rules()
    assert len(rules) == 3
    for rule in rules:
        assert any(rule["rule"].endswith(name) for name, _ in test_rules)
        assert any(rule["value"] == value for _, value in test_rules)

def test_save_ontology(validation_manager, tmp_path):
    """Test saving the ontology to a file."""
    validation_manager.add_validation_rule("SaveTest", "test save")
    save_path = tmp_path / "saved_validation_rules.ttl"
    validation_manager.save_ontology(str(save_path))
    
    assert save_path.exists()
    # Load the saved ontology and verify its contents
    new_manager = ValidationManager(str(save_path))
    rules = new_manager.get_validation_rules()
    assert len(rules) == 1
    assert rules[0]["rule"].endswith("SaveTest")
    assert rules[0]["value"] == "test save"

def test_save_ontology_without_path(validation_manager):
    """Test saving the ontology without specifying a path."""
    validation_manager.add_validation_rule("DefaultSaveTest", "test default save")
    validation_manager.save_ontology()
    # The file should be saved to the default location
    assert validation_manager.default_path.exists()
    # Load the saved ontology and verify its contents
    new_manager = ValidationManager()
    rules = new_manager.get_validation_rules()
    assert len(rules) == 1
    assert rules[0]["rule"].endswith("DefaultSaveTest")
    assert rules[0]["value"] == "test default save"

def test_save_ontology_to_invalid_path(validation_manager):
    """Test saving the ontology to an invalid path."""
    with pytest.raises(Exception):
        validation_manager.save_ontology("/nonexistent/directory/validation_rules.ttl") 