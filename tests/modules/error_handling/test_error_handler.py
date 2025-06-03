import pytest
from datetime import datetime
from typing import Any
from ontology_framework.modules.error_handling import (
    ErrorHandler,
    ErrorStep,
    ErrorSeverity,
    SecurityLevel,
    RiskLevel,
    ValidationRule
)

@pytest.fixture
def error_handler() -> ErrorHandler:
    return ErrorHandler()

def test_error_handler_initialization(error_handler: ErrorHandler) -> None:
    assert error_handler.current_step == ErrorStep.IDENTIFICATION
    assert len(error_handler.get_errors()) == 0
    assert isinstance(error_handler.get_metrics_report(), dict)
    assert isinstance(error_handler.get_compliance_report(), dict)

def test_add_error(error_handler: ErrorHandler) -> None:
    error_type = "TEST_ERROR"
    message = "Test error message"
    severity = "MEDIUM"
    
    error_handler.add_error(error_type, message, severity)
    errors = error_handler.get_errors()
    
    assert len(errors) == 1
    error = errors[0]
    assert error['type'] == error_type
    assert error['message'] == message
    assert error['severity'] == severity
    assert 'timestamp' in error
    assert isinstance(datetime.fromisoformat(error['timestamp']), datetime)

def test_metrics_tracking(error_handler: ErrorHandler) -> None:
    error_type = "TEST_ERROR"
    message = "Test error message"
    
    error_handler.add_error(error_type, message)
    metrics_report = error_handler.get_metrics_report()
    
    assert 'metrics' in metrics_report
    assert 'thresholds' in metrics_report
    assert 'timestamp' in metrics_report
    
    metrics = metrics_report['metrics']
    assert error_type in metrics['error_counts']
    assert metrics['error_counts'][error_type] == 1
    assert error_type in metrics['error_matrix']
    assert metrics['error_matrix'][error_type]['occurrences'] == 1
    assert metrics['error_matrix'][error_type]['total'] == 1

def test_compliance_tracking(error_handler: ErrorHandler) -> None:
    compliance_report = error_handler.get_compliance_report()
    
    assert 'ISO27001' in compliance_report
    assert 'GDPR' in compliance_report
    assert 'HIPAA' in compliance_report
    
    for standard in compliance_report.values():
        assert 'level' in standard
        assert 'requirements' in standard
        assert 'status' in standard

def test_rdf_serialization(error_handler: ErrorHandler) -> None:
    error_type = "TEST_ERROR"
    message = "Test error message"
    
    error_handler.add_error(error_type, message)
    rdf_data = error_handler.to_rdf()
    
    assert isinstance(rdf_data, str)
    assert error_type in rdf_data
    assert message in rdf_data

def test_validation_rules(error_handler: ErrorHandler) -> None:
    rule = ValidationRule(
        description="Test rule",
        severity="HIGH",
        message_template="Test message: {message}",
        rule_type="test"
    )
    
    assert error_handler.validation_handler.validate(rule, {"test": True})
    assert not error_handler.validation_handler.validate(rule, {"test": False})

def test_error_severity_validation(error_handler: ErrorHandler) -> None:
    # Test valid severity
    error_handler.add_error("TEST_ERROR", "Test message", "MEDIUM")
    assert len(error_handler.get_errors()) == 1
    
    # Test invalid severity
    error_handler.add_error("TEST_ERROR", "Test message", "INVALID")
    assert len(error_handler.get_errors()) == 1  # Should not add invalid error
