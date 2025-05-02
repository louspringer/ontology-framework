#!/usr/bin/env python3
"""Tests for ontology validation."""

import pytest
import logging
from pathlib import Path
from ontology_framework.validation.validation import OntologyValidator, ValidationError
import unittest
from rdflib import Graph
from ontology_framework.modules.error_handling.validation import ValidationHandler
from ontology_framework.modules.error_handling.types import (
    ValidationRuleType, ValidationRule, SecurityLevel, RiskLevel
)
from ontology_framework.modules.validation.bfg9k_pattern import BFG9KPattern
from ontology_framework.ontology_types import (
    ValidationRule, RiskLevel, SecurityLevel, ComplianceLevel
)

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

def test_risk_validation():
    handler = ValidationHandler()
    
    # Test valid risk data
    valid_data = {
        'risk_level': 'HIGH',
        'impact_assessment': 'Critical impact on system',
        'mitigation_measures': ['Backup', 'Redundancy'],
        'probability': 0.8,
        'severity': 0.9,
        'risk_score': 0.85
    }
    assert handler.validate(ValidationRule.RISK, valid_data)
    
    # Test invalid data types
    invalid_types = {
        'risk_level': 123,  # Should be string
        'impact_assessment': 123,  # Should be string
        'mitigation_measures': 'Backup',  # Should be list
        'probability': '0.8',  # Should be number
        'severity': '0.9',  # Should be number
        'risk_score': '0.85'  # Should be number
    }
    assert not handler.validate(ValidationRule.RISK, invalid_types)
    
    # Test out of range values
    out_of_range = {
        'risk_level': 'HIGH',
        'impact_assessment': 'Critical impact',
        'mitigation_measures': ['Backup'],
        'probability': 1.5,  # > 1.0
        'severity': -0.1,  # < 0
        'risk_score': 2.0  # > 1.0
    }
    assert not handler.validate(ValidationRule.RISK, out_of_range)
    
    # Test missing fields
    missing_fields = {
        'risk_level': 'HIGH',
        'impact_assessment': 'Critical impact'
        # Missing other required fields
    }
    assert not handler.validate(ValidationRule.RISK, missing_fields)

def test_security_validation():
    handler = ValidationHandler()
    
    # Test valid security data
    valid_data = {
        'security_level': 'HIGH',
        'authentication_method': 'OAuth2',
        'authorization_level': 'Admin',
        'data_classification': 'Confidential',
        'encryption_method': 'AES-256',
        'access_control': {'roles': ['Admin', 'User']},
        'audit_trail': True
    }
    assert handler.validate(ValidationRule.SECURITY, valid_data)
    
    # Test invalid security level
    invalid_level = {
        'security_level': 123,  # Should be string
        'authentication_method': 'OAuth2',
        'authorization_level': 'Admin',
        'data_classification': 'Confidential',
        'encryption_method': 'AES-256',
        'access_control': {'roles': ['Admin', 'User']},
        'audit_trail': True
    }
    assert not handler.validate(ValidationRule.SECURITY, invalid_level)
    
    # Test missing required fields
    missing_fields = {
        'security_level': 'HIGH',
        'authentication_method': 'OAuth2'
        # Missing other required fields
    }
    assert not handler.validate(ValidationRule.SECURITY, missing_fields)

def test_bfg9k_pattern_validation():
    handler = ValidationHandler()
    
    # Test valid BFG9K pattern data
    valid_data = {
        'ontology_id': 'test_ontology',
        'validation_type': 'strict',
        'security_level': 'high',
        'pattern_type': 'semantic',
        'pattern_elements': ['element1', 'element2'],
        'constraints': {
            'min_score': 0.8
        },
        'relationships': ['rel1', 'rel2'],
        'llm_config': {
            'model_type': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 1000
        }
    }
    assert handler.validate(ValidationRule.BFG9K, valid_data)

def test_validation_history():
    handler = ValidationHandler()
    
    # Perform multiple validations
    test_data = {
        'risk_level': 'HIGH',
        'impact_assessment': 'Critical impact',
        'mitigation_measures': ['Backup'],
        'probability': 0.8,
        'severity': 0.9,
        'risk_score': 0.85
    }
    
    # Test successful validation
    handler.validate(ValidationRule.RISK, test_data)
    history = handler.get_validation_history()
    assert len(history) == 1
    assert history[0]['rule'] == ValidationRule.RISK.value
    assert history[0]['result'] is True
    assert 'timestamp' in history[0]
    
    # Test failed validation
    invalid_data = {
        'risk_level': 123,  # Invalid type
        'impact_assessment': 'Critical impact',
        'mitigation_measures': ['Backup'],
        'probability': 0.8,
        'severity': 0.9,
        'risk_score': 0.85
    }
    handler.validate(ValidationRule.RISK, invalid_data)
    history = handler.get_validation_history()
    assert len(history) == 2
    assert history[1]['rule'] == ValidationRule.RISK.value
    assert history[1]['result'] is False
    assert 'timestamp' in history[1]
    assert 'error_details' in history[1]

class TestValidation(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.graph = Graph()
        self.graph.parse("guidance.ttl", format="turtle")
        self.handler = ValidationHandler(self.graph)
        self.bfg9k = BFG9KPattern(self.graph)

    def test_bfg9k_pattern_strict(self):
        """Test BFG9K pattern with strict conformance."""
        data = {
            'ontology_id': 'test_ontology',
            'validation_type': 'strict',
            'security_level': 'high',
            'pattern_type': 'semantic',
            'pattern_elements': ['element1', 'element2'],
            'constraints': {
                'min_score': 0.8
            },
            'relationships': ['rel1', 'rel2'],
            'llm_config': {
                'model_type': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 1000
            }
        }
        self.assertTrue(self.handler.validate(ValidationRule.BFG9K, data))

    def test_spore_validation(self):
        """Test SPORE pattern validation."""
        test_data = {
            "pattern_type": "SPORE",
            "pattern_elements": ["element1", "element2"],
            "constraints": {"constraint1": "value1"},
            "relationships": ["rel1", "rel2"]
        }
        
        rule = ValidationRule(
            description="Test SPORE validation",
            severity="HIGH",
            message_template="SPORE validation {result}",
            rule_type=ValidationRuleType.SPORE,
            conformance_level="STRICT"
        )
        
        result = self.handler.validate(rule, test_data)
        self.assertTrue(result)

    def test_semantic_validation(self):
        """Test semantic validation."""
        test_data = {
            "ontology_uri": "http://example.org/test",
            "class_hierarchy": {"class1": ["subclass1"]},
            "property_assertions": ["assertion1"]
        }
        
        rule = ValidationRule(
            description="Test semantic validation",
            severity="HIGH",
            message_template="Semantic validation {result}",
            rule_type=ValidationRuleType.SEMANTIC,
            conformance_level="STRICT"
        )
        
        result = self.handler.validate(rule, test_data)
        self.assertTrue(result)

    def test_syntax_validation(self):
        """Test syntax validation."""
        test_data = {
            "syntax_type": "turtle",
            "content": "@prefix : <http://example.org/> .",
            "format": "ttl"
        }
        
        rule = ValidationRule(
            description="Test syntax validation",
            severity="HIGH",
            message_template="Syntax validation {result}",
            rule_type=ValidationRuleType.SYNTAX,
            conformance_level="STRICT"
        )
        
        result = self.handler.validate(rule, test_data)
        self.assertTrue(result)

    def test_individual_type_validation(self):
        """Test individual type validation."""
        test_data = {
            "individual_uri": "http://example.org/individual1",
            "type_assertions": ["type1", "type2"],
            "property_values": {"prop1": "value1"}
        }
        
        rule = ValidationRule(
            description="Test individual type validation",
            severity="MEDIUM",
            message_template="Individual type validation {result}",
            rule_type=ValidationRuleType.INDIVIDUAL_TYPE,
            conformance_level="STRICT"
        )
        
        result = self.handler.validate(rule, test_data)
        self.assertTrue(result)

    def test_validation_history(self):
        """Test validation history tracking."""
        test_data = {
            "risk_level": RiskLevel.HIGH,
            "impact_assessment": "High impact",
            "mitigation_measures": ["measure1", "measure2"]
        }
        
        rule = ValidationRule(
            description="Test risk validation",
            severity="HIGH",
            message_template="Risk validation {result}",
            rule_type=ValidationRuleType.RISK,
            conformance_level="STRICT"
        )
        
        self.handler.validate(rule, test_data)
        history = self.handler.get_validation_history()
        
        self.assertGreater(len(history), 0)
        last_entry = history[-1]
        self.assertEqual(last_entry["rule"], rule.rule_type.name)
        self.assertEqual(last_entry["security_level"], "HIGH")

    def test_invalid_data(self):
        """Test validation with invalid data."""
        test_data = None
        
        rule = ValidationRule(
            description="Test validation with invalid data",
            severity="HIGH",
            message_template="Validation {result}",
            rule_type=ValidationRuleType.SECURITY,
            conformance_level="STRICT"
        )
        
        result = self.handler.validate(rule, test_data)
        self.assertFalse(result)

class TestValidationHandler(unittest.TestCase):
    def setUp(self):
        self.validator = ValidationHandler()
        self.test_graph = Graph()
        
    def test_risk_validation(self):
        data = {
            'risk_level': RiskLevel.HIGH,
            'impact_assessment': 'Critical impact on system',
            'mitigation_measures': ['Backup', 'Redundancy']
        }
        result = self.validator.validate(ValidationRule.RISK, data)
        self.assertTrue(result)
        
    def test_security_validation(self):
        data = {
            'security_level': SecurityLevel.HIGH,
            'authentication_method': 'OAuth2',
            'authorization_level': 'Admin',
            'data_classification': 'Confidential'
        }
        result = self.validator.validate(ValidationRule.SECURITY, data)
        self.assertTrue(result)
        
    def test_spore_validation(self):
        data = {
            'pattern_type': 'SPORE',
            'pattern_elements': ['Element1', 'Element2'],
            'constraints': {'constraint1': 'value1'},
            'relationships': ['rel1', 'rel2']
        }
        result = self.validator.validate(ValidationRule.SPORE, data)
        self.assertTrue(result)
        
    def test_semantic_validation(self):
        data = {
            'ontology_uri': 'http://example.com/ontology',
            'class_hierarchy': {'Class1': 'SuperClass'},
            'property_assertions': ['prop1', 'prop2']
        }
        result = self.validator.validate(ValidationRule.SEMANTIC, data)
        self.assertTrue(result)
        
    def test_syntax_validation(self):
        data = {
            'syntax_type': 'Turtle',
            'content': '@prefix : <http://example.com/> .',
            'format': 'text/turtle'
        }
        result = self.validator.validate(ValidationRule.SYNTAX, data)
        self.assertTrue(result)
        
    def test_individual_type_validation(self):
        data = {
            'individual_uri': 'http://example.com/individual1',
            'type_assertions': ['Type1', 'Type2'],
            'property_values': {'prop1': 'value1'}
        }
        result = self.validator.validate(ValidationRule.INDIVIDUAL_TYPE, data)
        self.assertTrue(result)
        
    def test_invalid_data(self):
        data = {'invalid': 'data'}
        result = self.validator.validate(ValidationRule.RISK, data)
        self.assertFalse(result)
        
    def test_none_data(self):
        result = self.validator.validate(ValidationRule.RISK, None)
        self.assertFalse(result)
        
    def test_invalid_rule(self):
        data = {'test': 'data'}
        with self.assertRaises(TypeError):
            self.validator.validate('invalid_rule', data)

if __name__ == '__main__':
    unittest.main() 