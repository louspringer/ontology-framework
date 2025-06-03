"""Tests for the validation handler."""

import pytest
from datetime import datetime
from typing import Dict, Any
from ontology_framework.modules.error_handling.validation import ValidationHandler
from ontology_framework.ontology_types import (
    ValidationRule,
    RiskLevel,
    SecurityLevel,
    ComplianceLevel
)

@pytest.fixture
def validation_handler():
    """Create a validation handler instance."""
    return ValidationHandler()

@pytest.fixture
def valid_risk_data():
    """Create valid risk data."""
    return {
        "level": "HIGH",
        "impact": 8,
        "probability": 7
    }

@pytest.fixture
def valid_security_data():
    return {
        'security_level': SecurityLevel.HIGH,
        'authentication_method': 'Two-factor authentication',
        'authorization_level': 'Admin',
        'data_classification': 'Confidential'
    }

@pytest.fixture
def valid_sensitive_data():
    return {
        'sensitive': True,
        'encryption_method': 'AES-256',
        'access_control_level': 'Restricted',
        'retention_period': 365
    }

@pytest.fixture
def valid_compliance_data():
    return {
        'compliance_level': ComplianceLevel.FULL,
        'requirements_met': ['GDPR', 'HIPAA'],
        'audit_date': datetime.now().isoformat(),
        'certification_status': 'Certified'
    }

@pytest.fixture
def valid_performance_data():
    return {
        "ontology_id": "test-ontology-002",
        "validation_type": "performance",
        "security_level": "MEDIUM",
        "pattern_type": "BFG9K",
        "pattern_elements": ["http://example.org/perf1", "http://example.org/perf2"],
        "constraints": {
            "min_score": 0.85
        },
        "relationships": ["http://example.org/rel1", "http://example.org/rel2"],
        "llm_config": {
            "model_type": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "response_time": 150,
        "throughput": 1000,
        "error_rate": 0.01
    }

@pytest.fixture
def valid_spore_data():
    """Create valid SPORE data."""
    return {
        "pattern_type": "test",
        "pattern_elements": ["element1", "element2"],
        "constraints": {
            "constraint1": "value1",
            "constraint2": "value2"
        }
    }

@pytest.fixture
def valid_semantic_data():
    """Create valid semantic data."""
    return {
        "ontology_id": "test_ontology",
        "validation_type": "semantic",
        "data_format": "turtle"
    }

@pytest.fixture
def valid_syntax_data():
    """Create valid syntax data."""
    return {
        "code": "def test(): pass",
        "language": "python",
        "version": "3.8"
    }

@pytest.fixture
def valid_individual_type_data():
    """Create valid individual type data."""
    return {
        "individual_uri": "http://example.org/test#individual1",
        "type_assertions": ["type1", "type2"],
        "property_values": {
            "prop1": "value1",
            "prop2": "value2"
        }
    }

def test_validate_risk(validation_handler, valid_risk_data):
    """Test risk validation."""
    result = validation_handler.validate(ValidationRule.RISK, valid_risk_data)
    assert result is True

def test_validate_security(validation_handler, valid_security_data):
    """Test security validation."""
    result = validation_handler.validate(ValidationRule.SECURITY, valid_security_data)
    assert result is True

def test_validate_sensitive_data(validation_handler, valid_sensitive_data):
    """Test sensitive data validation."""
    result = validation_handler.validate(ValidationRule.SENSITIVE_DATA, valid_sensitive_data)
    assert result is True

def test_validate_compliance():
    """Test compliance validation."""
    handler = ValidationHandler()
    data = {
        'compliance_level': 'HIGH',
        'status': 'COMPLIANT',
        'requirements': ['REQ-001', 'REQ-002'],
        'review_date': '2025-01-01',
        'evidence': {
            'REQ-001': 'Evidence for requirement 1',
            'REQ-002': 'Evidence for requirement 2'
        }
    }
    result = handler.validate(ValidationRule.COMPLIANCE, data)
    assert result is True

def test_validate_performance_basic():
    """Test basic performance validation."""
    handler = ValidationHandler()
    valid_data = {
        "response_time": 0.5,
        "throughput": 100,
        "error_rate": 0.01,
        "resource_usage": {
            "cpu": 50,
            "memory": 70,
            "disk": 30
        }
    }
    result = handler.validate(ValidationRule.PERFORMANCE, valid_data)
    assert result is True

def test_validate_spore(validation_handler, valid_spore_data):
    """Test SPORE validation."""
    result = validation_handler.validate(ValidationRule.SPORE, valid_spore_data)
    assert result is True

def test_validate_semantic(validation_handler, valid_semantic_data):
    """Test semantic validation."""
    result = validation_handler.validate(ValidationRule.SEMANTIC, valid_semantic_data)
    assert result is True

def test_validate_syntax(validation_handler, valid_syntax_data):
    """Test syntax validation."""
    result = validation_handler.validate(ValidationRule.SYNTAX, valid_syntax_data)
    assert result is True

def test_validate_individual_type(validation_handler, valid_individual_type_data):
    """Test individual type validation."""
    result = validation_handler.validate(ValidationRule.INDIVIDUAL_TYPE, valid_individual_type_data)
    assert result is True

def test_validate_with_invalid_data(validation_handler):
    """Test validation with invalid data."""
    invalid_data = {}
    for rule in ValidationRule:
        result = validation_handler.validate(rule, invalid_data)
        assert result is False

def test_validate_with_missing_fields(validation_handler, valid_risk_data):
    """Test validation with missing fields."""
    incomplete_data = valid_risk_data.copy()
    del incomplete_data['level']
    result = validation_handler.validate(ValidationRule.RISK, incomplete_data)
    assert result is False

def test_validate_with_invalid_types():
    """Test validation with invalid types."""
    handler = ValidationHandler()
    data = {
        'level': 123,  # Should be string
        'impact': 'high',  # Should be number
        'probability': 'medium',  # Should be number
        'security_level': 'low',  # Should be SecurityLevel enum
        'compliance_level': 'partial',  # Should be ComplianceLevel enum
        'resource_usage': {
            'cpu': 'high',  # Should be float between 0 and 1
            'memory': 'low'  # Should be float between 0 and 1
        }
    }
    result = handler.validate(ValidationRule.RISK, data)
    assert result is False

def test_validation_history_basic():
    """Test basic validation history."""
    handler = ValidationHandler()
    data = {
        "level": "HIGH",
        "impact": 8,
        "probability": 7
    }
    result = handler.validate(ValidationRule.RISK, data)
    history = handler.get_validation_history()
    assert len(history) == 1
    assert history[0]["rule"] == ValidationRule.RISK.value
    assert history[0]["result"] is True
    assert history[0]["priority"] == ValidationRule.RISK.priority
    assert history[0]["target"] == ValidationRule.RISK.target
    assert history[0]["validator"] == ValidationRule.RISK.validator

def test_validate_performance_advanced():
    """Test advanced performance validation."""
    handler = ValidationHandler()
    data = {
        "response_time": 0.3,
        "throughput": 1000,
        "error_rate": 0.01,
        "resource_usage": {
            "cpu": 0.5,
            "memory": 0.7,
            "disk": 0.3
        }
    }
    result = handler.validate(ValidationRule.PERFORMANCE, data)
    assert result is True

def test_validation_history_advanced():
    """Test advanced validation history."""
    handler = ValidationHandler()
    risk_data = {"level": "HIGH", "impact": 8, "probability": 7}
    security_data = {
        "security_level": SecurityLevel.HIGH,
        "authentication_method": "2FA",
        "authorization_level": "Admin",
        "data_classification": "Confidential"
    }
    
    risk_result = handler.validate(ValidationRule.RISK, risk_data)
    security_result = handler.validate(ValidationRule.SECURITY, security_data)
    
    history = handler.get_validation_history()
    assert len(history) == 2
    assert history[0]["rule"] == ValidationRule.RISK.value
    assert history[1]["rule"] == ValidationRule.SECURITY.value
    assert history[0]["result"] is True
    assert history[1]["result"] is True

def test_invalid_rule():
    """Test validation with invalid rule."""
    handler = ValidationHandler()
    data = {"test": "data"}
    with pytest.raises(ValueError, match="Rule INVALID_RULE not found"):
        handler.validate("INVALID_RULE", data)

def test_validation_rule_properties():
    """Test validation rule properties."""
    assert ValidationRule.RISK.priority == "HIGH"
    assert ValidationRule.PERFORMANCE.priority == "MEDIUM"
    assert ValidationRule.RISK.target == "data"
    assert ValidationRule.BFG9K.target == "pattern"
    assert ValidationRule.RISK.validator == "risk_validator"
    assert ValidationRule.PERFORMANCE.validator == "performance_validator"

def test_validation_with_valid_data():
    """Test validation with valid data."""
    handler = ValidationHandler()
    data = {
        "level": "HIGH",
        "impact": 8,
        "probability": 7
    }
    result = handler.validate(ValidationRule.RISK, data)
    assert result is True

def test_rule_not_found():
    """Test validation with non-existent rule."""
    handler = ValidationHandler()
    data = {'test': 'data'}
    with pytest.raises(ValueError, match="Rule NONEXISTENT_RULE not found"):
        handler.validate("NONEXISTENT_RULE", data)

def test_validate_with_empty_data():
    """Test validation with empty data."""
    handler = ValidationHandler()
    data = {}
    result = handler.validate(ValidationRule.RISK, data)
    assert result is False

def test_validate_with_none_data():
    """Test validation with None data."""
    handler = ValidationHandler()
    with pytest.raises(TypeError):
        handler.validate(ValidationRule.RISK, None)

def test_validate_with_invalid_conformance_level():
    """Test validation with invalid conformance level."""
    handler = ValidationHandler()
    data = {
        "level": "INVALID",
        "impact": 8,
        "probability": 7
    }
    result = handler.validate(ValidationRule.RISK, data)
    assert result is False

def test_validation_history_with_error():
    """Test validation history with error."""
    handler = ValidationHandler()
    data = {
        "level": "HIGH",
        "impact": "invalid",  # Should be a number
        "probability": 7
    }
    result = handler.validate(ValidationRule.RISK, data)
    history = handler.get_validation_history()
    assert len(history) == 1
    assert history[0]["result"] is False
    assert history[0]["error_message"] is not None

def test_validate_with_partial_data():
    """Test validation with partial data."""
    handler = ValidationHandler()
    data = {
        "response_time": 0.5,
        # Missing throughput and error_rate
    }
    result = handler.validate(ValidationRule.PERFORMANCE, data)
    assert result is False

def test_validate_with_boundary_values():
    """Test validation with boundary values."""
    handler = ValidationHandler()
    data = {
        "response_time": 0,  # Minimum valid value
        "throughput": 1,     # Minimum valid value
        "error_rate": 0,     # Minimum valid value
        "resource_usage": {
            "cpu": 0,        # Minimum valid value
            "memory": 0,     # Minimum valid value
            "disk": 0        # Minimum valid value
        }
    }
    result = handler.validate(ValidationRule.PERFORMANCE, data)
    assert result is True

def test_validate_with_invalid_resource_usage():
    """Test validation with invalid resource usage."""
    handler = ValidationHandler()
    data = {
        "response_time": 0.5,
        "throughput": 100,
        "error_rate": 0.01,
        "resource_usage": {
            "cpu": 1.5,  # Invalid: should be between 0 and 1
            "memory": 0.7
        }
    }
    result = handler.validate(ValidationRule.PERFORMANCE, data)
    assert result is False

def test_validation_history_clear():
    """Test clearing validation history."""
    handler = ValidationHandler()
    data = {"level": "HIGH", "impact": 8, "probability": 7}
    handler.validate(ValidationRule.RISK, data)
    handler._validation_history.clear()
    assert len(handler.get_validation_history()) == 0

def test_filter_validation_history():
    """Test filtering validation history."""
    handler = ValidationHandler()
    handler.validate(ValidationRule.RISK, {"level": "HIGH"})
    handler.validate(ValidationRule.SECURITY, {"security_level": SecurityLevel.HIGH})
    
    risk_history = [h for h in handler.get_validation_history() if h["rule"] == ValidationRule.RISK.value]
    assert len(risk_history) == 1
    assert risk_history[0]["rule"] == ValidationRule.RISK.value

def test_get_validation_statistics():
    """Test getting validation statistics."""
    handler = ValidationHandler()
    handler.validate(ValidationRule.RISK, {"level": "HIGH", "impact": 8, "probability": 7})
    handler.validate(ValidationRule.RISK, {"level": "INVALID"})
    
    stats = handler.get_validation_statistics()
    assert stats["total_validations"] == 2
    assert stats["successful_validations"] == 1
    assert stats["failed_validations"] == 1

def test_add_custom_rule():
    """Test adding custom validation rule."""
    handler = ValidationHandler()
    
    def custom_validator(data: Dict[str, Any]) -> bool:
        return isinstance(data.get("value"), int) and data["value"] > 0
    
    handler.add_custom_rule("positive_integer", custom_validator)
    valid_data = {"value": 42}
    invalid_data = {"value": -1}
    
    assert handler.validate("positive_integer", valid_data) is True
    assert handler.validate("positive_integer", invalid_data) is False

def test_configure_validation_threshold():
    """Test configuring validation threshold."""
    handler = ValidationHandler()
    
    def threshold_check(data: Dict[str, Any]) -> bool:
        """Check if risk level meets threshold."""
        return data.get('level', 'LOW') == 'HIGH'
        
    handler.configure_validation_threshold(ValidationRule.RISK, 0.8, threshold_check)
    
    # Test with data that meets threshold
    high_risk_data = {'level': 'HIGH', 'impact': 8, 'probability': 7}
    result = handler.validate(ValidationRule.RISK, high_risk_data)
    assert result is True
    
    # Test with data that doesn't meet threshold
    low_risk_data = {'level': 'LOW', 'impact': 2, 'probability': 1}
    result = handler.validate(ValidationRule.RISK, low_risk_data)
    assert result is False

def test_export_validation_history():
    """Test exporting validation history."""
    handler = ValidationHandler()
    handler.validate(ValidationRule.RISK, {"level": "HIGH"})
    
    json_export = handler.export_validation_history("json")
    assert isinstance(json_export, str)
    assert "rule" in json_export
    assert "result" in json_export
    
    csv_export = handler.export_validation_history("csv")
    assert isinstance(csv_export, str)
    assert "rule,result" in csv_export

def test_generate_validation_report():
    """Test generating validation report."""
    handler = ValidationHandler()
    
    # Add some validation entries
    data = {'level': 'HIGH', 'impact': 8, 'probability': 7}
    handler.validate(ValidationRule.RISK, data)
    
    data = {'compliance_level': 'HIGH', 'status': 'COMPLIANT', 'requirements': ['REQ-001']}
    handler.validate(ValidationRule.COMPLIANCE, data)
    
    report = handler.generate_validation_report()
    
    # Check report structure
    assert "summary" in report
    assert "error_distribution" in report
    assert "rule_distribution" in report
    assert "validation_history" in report
    assert "recent_validations" in report
    
    # Check summary statistics
    assert report["summary"]["total_validations"] == 2
    assert isinstance(report["summary"]["success_rate"], float)
    
    # Check distributions
    assert isinstance(report["error_distribution"], dict)
    assert isinstance(report["rule_distribution"], dict)
    
    # Check history
    assert isinstance(report["validation_history"], list)
    assert len(report["validation_history"]) == 2
    
    # Check recent validations
    assert isinstance(report["recent_validations"], list)
    assert len(report["recent_validations"]) <= 10
