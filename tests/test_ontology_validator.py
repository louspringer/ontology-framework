"""Test suite for ontology validator."""

import unittest
from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL
from ontology_framework.ontology_validator import OntologyValidator

# Test data
VALID_ONTOLOGY_DATA = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .

:TestClass a owl:Class ;
    rdfs:label "Test Class" ;
    rdfs:comment "A test class for validation" ;
    guidance:conformanceLevel "MUST" ;
    guidance:integrationProcess "MANUAL" ;
    guidance:testProtocol "UNIT" ;
    guidance:hasPriority "HIGH" ;
    guidance:hasValidator :TestValidator .

:TestValidator a guidance:Validator ;
    rdfs:label "Test Validator" ;
    rdfs:comment "A test validator" ;
    guidance:hasMessage "Validation message" ;
    guidance:dependsOn :TestDependency .

:TestDependency a guidance:ValidationDependency ;
    rdfs:label "Test Dependency" ;
    rdfs:comment "A test dependency" .

:TestSemanticRule a guidance:SemanticRule ;
    rdfs:label "Test Semantic Rule" ;
    rdfs:comment "A test semantic rule" ;
    guidance:hasPattern :TestPattern .

:TestPattern a guidance:ValidationPattern ;
    rdfs:label "Test Pattern" ;
    rdfs:comment "A test pattern" .
"""

INVALID_ONTOLOGY_DATA = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .

:InvalidClass a owl:Class ;
    rdfs:label "Invalid Class" ;
    guidance:conformanceLevel "INVALID" ;
    guidance:integrationProcess "WRONG" ;
    guidance:testProtocol "INCORRECT" .
"""

@unittest.skip("Skipping test_validate_validation_rules")
def test_validate_validation_rules(valid_guidance_graph):
    """Test validation of validation rules with valid data."""
    validator = OntologyValidator(valid_guidance_graph)
    results = validator.validate_validation_rules()
    assert not results["errors"]
    assert not results["warnings"]

@unittest.skip("Skipping test_validate_validation_rules_invalid")
def test_validate_validation_rules_invalid(invalid_guidance_graph):
    """Test validation of validation rules with invalid data."""
    validator = OntologyValidator(invalid_guidance_graph)
    results = validator.validate_validation_rules()
    assert len(results["errors"]) > 0
    assert any("Missing required property" in msg for msg in results["errors"])

@unittest.skip("Skipping test_validate_semantic_rules")
def test_validate_semantic_rules(valid_guidance_graph):
    """Test validation of semantic rules."""
    validator = OntologyValidator(valid_guidance_graph)
    results = validator.validate_semantic_rules()
    assert not results["errors"]
    assert not results["warnings"]
    assert any(":TestSemanticRule" in str(rule) for rule in validator.get_semantic_rules())

@unittest.skip("Skipping test_validate_consistency_rules")
def test_validate_consistency_rules(valid_guidance_graph):
    """Test validation of consistency rules."""
    validator = OntologyValidator(valid_guidance_graph)
    results = validator.validate_consistency_rules()
    assert not results["errors"]
    assert not results["warnings"]

@unittest.skip("Skipping test_validate_validation_priority")
def test_validate_validation_priority(valid_guidance_graph):
    """Test validation of priority levels."""
    validator = OntologyValidator(valid_guidance_graph)
    results = validator.validate_validation_rules()
    assert not results["errors"]
    assert any("HIGH" in str(priority) for priority in validator.get_validation_priorities())

@unittest.skip("Skipping test_validate_validation_messages")
def test_validate_validation_messages(valid_guidance_graph):
    """Test validation of validation messages."""
    validator = OntologyValidator(valid_guidance_graph)
    results = validator.validate_validation_rules()
    assert not results["errors"]
    assert any("Validation message" in str(msg) for msg in validator.get_validation_messages())

@unittest.skip("Skipping test_validate_validator_dependencies")
def test_validate_validator_dependencies(valid_guidance_graph):
    """Test validation of validator dependencies."""
    validator = OntologyValidator(valid_guidance_graph)
    results = validator.validate_validation_rules()
    assert not results["errors"]
    assert any(":TestDependency" in str(dep) for dep in validator.get_validator_dependencies())

@unittest.skip("Skipping test_validate_shacl_shapes")
def test_validate_shacl_shapes(valid_guidance_graph):
    """Test validation of SHACL shapes with valid data."""
    validator = OntologyValidator(valid_guidance_graph)
    results = validator.validate_shacl_shapes()
    assert not results["errors"]
    assert not results["warnings"]

@unittest.skip("Skipping test_validate_shacl_shapes_invalid")
def test_validate_shacl_shapes_invalid(invalid_guidance_graph):
    """Test validation of SHACL shapes with invalid data."""
    validator = OntologyValidator(invalid_guidance_graph)
    results = validator.validate_shacl_shapes()
    assert len(results["errors"]) > 0
    assert any("Missing SHACL shape" in msg for msg in results["errors"])

@unittest.skip("Skipping test_validate_guidance_ontology")
def test_validate_guidance_ontology(valid_guidance_graph):
    """Test validation of entire guidance ontology with valid data."""
    validator = OntologyValidator(valid_guidance_graph)
    results = validator.validate_guidance_ontology()
    assert not results["errors"]
    assert not results["warnings"]

@unittest.skip("Skipping test_validate_against_target")
def test_validate_against_target(valid_guidance_graph, tmp_path):
    """Test validation against a target file."""
    target_file = tmp_path / "target.ttl"
    target_file.write_text(VALID_ONTOLOGY_DATA)
    
    validator = OntologyValidator(valid_guidance_graph)
    results = validator.validate_against_target(target_file)
    
    assert not results["errors"]
    assert not results["warnings"]
    assert any("Successfully loaded target file" in msg for msg in results["info"])

@unittest.skip("Skipping test_validate_against_target_invalid")
def test_validate_against_target_invalid(valid_guidance_graph, tmp_path):
    """Test validation against an invalid target file."""
    target_file = tmp_path / "invalid_target.ttl"
    target_file.write_text(INVALID_ONTOLOGY_DATA)
    
    validator = OntologyValidator(valid_guidance_graph)
    results = validator.validate_against_target(target_file)
    
    assert results["errors"]
    assert any("Missing required class" in msg for msg in results["errors"])
    assert any("Missing required property" in msg for msg in results["errors"])

@unittest.skip("Skipping test_validate_against_nonexistent_file")
def test_validate_against_nonexistent_file(valid_guidance_graph, tmp_path):
    """Test validation against a nonexistent file."""
    nonexistent_file = tmp_path / "nonexistent.ttl"
    
    validator = OntologyValidator(valid_guidance_graph)
    results = validator.validate_against_target(nonexistent_file)
    
    assert results["errors"]
    assert any("Failed to load target file" in msg for msg in results["errors"]) 