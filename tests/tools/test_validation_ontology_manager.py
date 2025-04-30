import pytest
from pathlib import Path
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from ontology_framework.tools.validation_ontology_manager import ValidationOntologyManager

@pytest.fixture
def validation_manager():
    return ValidationOntologyManager()

def test_validation_structure_setup(validation_manager):
    """Test that the core validation structure is properly initialized."""
    # Verify core classes exist
    assert validation_manager.validation_rule_class is not None
    assert validation_manager.validation_level_class is not None
    
    # Verify properties exist
    assert validation_manager.has_level is not None
    assert validation_manager.has_description is not None
    
    # Check class types using SPARQL
    query = """
    ASK {
        ?validationRule a owl:Class .
        ?validationLevel a owl:Class .
    }
    """
    assert validation_manager.execute_sparql_query(query)

def test_add_validation_rule(validation_manager):
    """Test adding a new validation rule."""
    rule_uri = validation_manager.add_validation_rule(
        "TEST001",
        "Test validation rule",
        "HIGH"
    )
    
    # Verify rule exists using SPARQL
    query = """
    ASK {
        ?rule a ?validationRule ;
              ?hasDescription "Test validation rule" ;
              ?hasLevel ?level .
        ?level a ?validationLevel .
    }
    """
    assert validation_manager.execute_sparql_query(query)

def test_get_validation_rules(validation_manager):
    """Test retrieving validation rules."""
    # Add test rules
    validation_manager.add_validation_rule(
        "TEST001",
        "First test rule",
        "HIGH"
    )
    validation_manager.add_validation_rule(
        "TEST002",
        "Second test rule",
        "MEDIUM"
    )
    
    rules = validation_manager.get_validation_rules()
    assert len(rules) == 2
    assert any(r["description"] == "First test rule" for r in rules)
    assert any(r["description"] == "Second test rule" for r in rules)
    assert any(r["level"] == "Level_HIGH" for r in rules)
    assert any(r["level"] == "Level_MEDIUM" for r in rules)

def test_validate_rule_exists(validation_manager):
    """Test checking for rule existence."""
    rule_id = "TEST001"
    validation_manager.add_validation_rule(
        rule_id,
        "Test rule",
        "LOW"
    )
    
    assert validation_manager.validate_rule_exists(rule_id)
    assert not validation_manager.validate_rule_exists("NONEXISTENT")

def test_get_validation_rules_empty(validation_manager):
    """Test getting validation rules when none exist."""
    rules = validation_manager.get_validation_rules()
    assert len(rules) == 0

def test_validation_rule_properties(validation_manager):
    """Test validation rule property values and types."""
    rule_uri = validation_manager.add_validation_rule(
        "TEST003",
        "Test property values",
        "HIGH"
    )
    
    # Verify property values using direct graph access
    for _, _, obj in validation_manager.graph.triples((rule_uri, RDF.type, None)):
        assert obj == validation_manager.validation_rule_class
        
    for _, _, obj in validation_manager.graph.triples((rule_uri, validation_manager.has_description, None)):
        assert isinstance(obj, Literal)
        assert str(obj) == "Test property values"
        
    level_found = False
    for _, _, obj in validation_manager.graph.triples((rule_uri, validation_manager.has_level, None)):
        assert str(obj).endswith("Level_HIGH")
        level_found = True
    assert level_found

def test_sparql_query_error_handling(validation_manager):
    """Test error handling in SPARQL queries."""
    with pytest.raises(Exception):
        validation_manager.execute_sparql_query("INVALID SPARQL QUERY {")

def test_duplicate_rule_handling(validation_manager):
    """Test adding a rule with the same ID."""
    rule_id = "TEST001"
    validation_manager.add_validation_rule(rule_id, "First rule", "HIGH")
    validation_manager.add_validation_rule(rule_id, "Updated rule", "MEDIUM")
    
    rules = validation_manager.get_validation_rules()
    matching_rules = [r for r in rules if r["rule"].endswith(rule_id)]
    assert len(matching_rules) == 1
    assert matching_rules[0]["description"] == "Updated rule"
    assert matching_rules[0]["level"] == "Level_MEDIUM" 