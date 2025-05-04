import pytest
from pathlib import Path
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from ontology_framework.tools.validation_ontology_manager import ValidationOntologyManager

@pytest.fixture
def validation_manager():
    """Create a validation manager instance."""
    manager = ValidationOntologyManager()
    yield manager
    # Cleanup: Clear the validation repository
    manager.client.clear_graph()

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
    """Test adding a validation rule."""
    rule_id = "TEST_RULE_001"
    description = "Test validation rule"
    level = "HIGH"
    
    rule_uri = validation_manager.add_validation_rule(rule_id, description, level)
    assert isinstance(rule_uri, URIRef)
    assert str(rule_uri).endswith(f"Rule_{rule_id}")
    
    # Verify the rule exists
    assert validation_manager.validate_rule_exists(rule_id)

def test_get_validation_rules(validation_manager):
    """Test retrieving validation rules."""
    # Add some test rules
    validation_manager.add_validation_rule("RULE_001", "First rule", "HIGH")
    validation_manager.add_validation_rule("RULE_002", "Second rule", "MEDIUM")
    
    rules = validation_manager.get_validation_rules()
    assert len(rules) >= 2
    
    # Find our test rules
    rule_001 = next((r for r in rules if r["rule"].endswith("Rule_RULE_001")), None)
    rule_002 = next((r for r in rules if r["rule"].endswith("Rule_RULE_002")), None)
    
    assert rule_001 is not None
    assert rule_002 is not None
    assert rule_001["description"] == "First rule"
    assert rule_002["description"] == "Second rule"
    assert rule_001["level"] == "Level_HIGH"
    assert rule_002["level"] == "Level_MEDIUM"

def test_validate_rule_exists(validation_manager):
    """Test rule existence validation."""
    # Add a test rule
    validation_manager.add_validation_rule("EXISTENCE_TEST", "Test rule", "LOW")
    
    # Check that it exists
    assert validation_manager.validate_rule_exists("EXISTENCE_TEST")
    
    # Check that a non-existent rule doesn't exist
    assert not validation_manager.validate_rule_exists("NON_EXISTENT_RULE")

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

def test_update_validation_rule(validation_manager):
    """Test updating an existing validation rule."""
    rule_id = "UPDATE_TEST"
    
    # Add initial rule
    validation_manager.add_validation_rule(rule_id, "Initial description", "LOW")
    
    # Update the rule
    validation_manager.add_validation_rule(rule_id, "Updated description", "HIGH")
    
    # Get the rules and verify the update
    rules = validation_manager.get_validation_rules()
    updated_rule = next((r for r in rules if r["rule"].endswith(f"Rule_{rule_id}")), None)
    
    assert updated_rule is not None
    assert updated_rule["description"] == "Updated description"
    assert updated_rule["level"] == "Level_HIGH" 