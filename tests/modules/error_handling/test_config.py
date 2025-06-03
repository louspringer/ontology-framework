"""Tests for validation configuration."""

import pytest
from ontology_framework.modules.error_handling.validation import ValidationHandler
from ontology_framework.ontology_types import (
    ValidationRule, ErrorSeverity, SecurityLevel, RiskLevel,
    ComplianceLevel
)

def test_validation_rules_configuration():
    """Test validation rules are properly configured."""
    handler = ValidationHandler()
    
    # Verify all required validation rules are present
    required_rules = {
        ValidationRule.RISK,
        ValidationRule.SECURITY,
        ValidationRule.SENSITIVE_DATA,
        ValidationRule.COMPLIANCE,
        ValidationRule.PERFORMANCE
    }
    
    configured_rules = set(handler.validation_rules.keys())
    assert configured_rules == required_rules, \
        f"Missing rules: {required_rules - configured_rules}"
    
    # Verify each validation function exists and is callable
    for rule, func in handler.validation_rules.items():
        assert callable(func), f"Validation function for {rule.value} is not callable"

def test_validation_rule_inputs():
    """Test validation rules handle various input types correctly."""
    handler = ValidationHandler()
    
    # Test with None
    for rule in handler.validation_rules:
        assert not handler.validate(rule, None)
    
    # Test with empty dict
    for rule in handler.validation_rules:
        assert not handler.validate(rule, {})
    
    # Test with non-dict
    invalid_inputs = [
        42,
        "string",
        [1, 2, 3],
        (1, 2),
        {1, 2, 3},
        True
    ]
    for rule in handler.validation_rules:
        for invalid_input in invalid_inputs:
            assert not handler.validate(rule, invalid_input)

def test_validation_history_integrity():
    """Test validation history maintains integrity."""
    handler = ValidationHandler()
    
    # Initial history should be empty
    assert len(handler.get_validation_history()) == 0
    
    # Perform validations
    test_data = {
        ValidationRule.RISK: {
            'risk_level': RiskLevel.HIGH,
            'impact_assessment': 'test',
            'mitigation_measures': []
        },
        ValidationRule.SECURITY: {
            'security_level': SecurityLevel.HIGH,
            'authentication_method': 'test',
            'authorization_level': 'test',
            'data_classification': 'test'
        }
    }
    
    # Track expected results
    expected_results = []
    
    # Perform validations and track results
    for rule, data in test_data.items():
        result = handler.validate(rule, data)
        expected_results.append({
            'rule': rule.value,
            'result': result
        })
    
    # Verify history
    history = handler.get_validation_history()
    assert len(history) == len(expected_results)
    
    for i, expected in enumerate(expected_results):
        assert history[i]['rule'] == expected['rule']
        assert history[i]['result'] == expected['result']
        assert 'timestamp' in history[i]
        assert isinstance(history[i]['timestamp'], str)

def test_validation_history_immutability():
    """Test validation history cannot be modified externally."""
    handler = ValidationHandler()
    
    # Get initial history
    history1 = handler.get_validation_history()
    
    # Perform a validation
    handler.validate(ValidationRule.RISK, {
        'risk_level': RiskLevel.HIGH,
        'impact_assessment': 'test',
        'mitigation_measures': []
    })
    
    # Get updated history
    history2 = handler.get_validation_history()
    
    # Verify histories are different objects
    assert history1 is not history2
    
    # Try to modify history
    history2.append({'test': 'test'})
    
    # Verify original history is unchanged
    current_history = handler.get_validation_history()
    assert len(current_history) == 1
    assert 'test' not in current_history[-1]

def test_validation_error_handling():
    """Test validation error handling."""
    handler = ValidationHandler()
    
    # Test with invalid rule type
    with pytest.raises(TypeError):
        handler.validate(None, {})
    
    with pytest.raises(TypeError):
        handler.validate(42, {})
    
    with pytest.raises(TypeError):
        handler.validate("INVALID", {})
