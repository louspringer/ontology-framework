"""Test suite for error handler."""

import unittest
from typing import Dict, List, Optional
from datetime import datetime
from ontology_framework.error_handler import ErrorHandler
from ontology_framework.ontology_types import (
    ErrorType, ErrorSeverity, ErrorStep, ValidationRule,
    SecurityLevel, ComplianceLevel, RiskLevel, PerformanceMetric
)

def test_error_handling_steps() -> None:
    handler = ErrorHandler()
    
    # Verify step order
    assert handler.STEP_ORDER[ErrorStep.IDENTIFICATION] == 1
    assert handler.STEP_ORDER[ErrorStep.ANALYSIS] == 2
    assert handler.STEP_ORDER[ErrorStep.RECOVERY] == 3
    assert handler.STEP_ORDER[ErrorStep.PREVENTION] == 4
    assert handler.STEP_ORDER[ErrorStep.MONITORING] == 5
    assert handler.STEP_ORDER[ErrorStep.REPORTING] == 6
    assert handler.STEP_ORDER[ErrorStep.DOCUMENTATION] == 7
    assert handler.STEP_ORDER[ErrorStep.REVIEW] == 8
    assert handler.STEP_ORDER[ErrorStep.CLOSURE] == 9

def test_error_handling_validations() -> None:
    handler = ErrorHandler()
    
    # Verify validation rules
    assert ValidationRule.SENSITIVE_DATA in handler.validation_rules
    assert ValidationRule.RISK in handler.validation_rules
    assert ValidationRule.MATRIX in handler.validation_rules
    assert ValidationRule.COMPLIANCE in handler.validation_rules
    assert ValidationRule.SECURITY in handler.validation_rules
    assert ValidationRule.PERFORMANCE in handler.validation_rules
    assert ValidationRule.RELIABILITY in handler.validation_rules
    assert ValidationRule.AVAILABILITY in handler.validation_rules
    assert ValidationRule.SCALABILITY in handler.validation_rules
    assert ValidationRule.MAINTAINABILITY in handler.validation_rules
    assert ValidationRule.SEVERITY in handler.validation_rules
    assert ValidationRule.STEP_ORDER in handler.validation_rules

def test_error_prevention_and_recovery() -> None:
    handler = ErrorHandler()
    
    # Verify prevention measures
    assert "ErrorBoundary" in handler.prevention_measures
    assert "InputValidation" in handler.prevention_measures
    assert "AutomaticRetry" in handler.prevention_measures
    assert "Checkpoint" in handler.prevention_measures
    assert "CircuitBreaker" in handler.prevention_measures
    assert "RateLimiting" in handler.prevention_measures
    assert "ResourceQuotas" in handler.prevention_measures
    assert "AccessControl" in handler.prevention_measures
    
    # Verify recovery strategies
    assert "AutomaticFailover" in handler.recovery_strategies
    assert "DataReplication" in handler.recovery_strategies
    assert "StateRecovery" in handler.recovery_strategies
    assert "ServiceRestart" in handler.recovery_strategies

def test_error_type_hierarchy() -> None:
    handler = ErrorHandler()
    
    # Verify error type hierarchy
    assert handler.ERROR_HIERARCHY[ErrorType.VALIDATION] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.CONFIGURATION] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.NETWORK] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.DATABASE] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.FILE_SYSTEM] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.MEMORY] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.CPU] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.DISK] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.API] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.AUTHENTICATION] == ErrorType.SECURITY
    assert handler.ERROR_HIERARCHY[ErrorType.AUTHORIZATION] == ErrorType.SECURITY
    assert handler.ERROR_HIERARCHY[ErrorType.COMPLIANCE] == ErrorType.SECURITY
    assert handler.ERROR_HIERARCHY[ErrorType.SECURITY] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.PERFORMANCE] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.SCALABILITY] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.AVAILABILITY] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.RELIABILITY] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.MAINTAINABILITY] == ErrorType.RUNTIME
    assert handler.ERROR_HIERARCHY[ErrorType.DATA_LOSS] == ErrorType.RUNTIME

def test_error_handling_process() -> None:
    """Test the complete error handling process."""
    handler = ErrorHandler()
    
    # Add an error
    success = handler.add_error(
        error_type=ErrorType.VALIDATION,
        message="Test validation error",
        severity=ErrorSeverity.ERROR,
        step=ErrorStep.IDENTIFICATION,
        risk_level=RiskLevel.MEDIUM,
        security_level=SecurityLevel.MEDIUM
    )
    
    assert success
    assert len(handler.errors) == 1
    
    # Verify error properties
    error = handler.errors[0]
    assert error["type"] == ErrorType.VALIDATION
    assert error["parent_type"] == ErrorType.RUNTIME
    assert error["message"] == "Test validation error"
    assert error["severity"] == ErrorSeverity.ERROR
    assert error["step"] == ErrorStep.IDENTIFICATION
    assert error["risk_level"] == RiskLevel.MEDIUM
    assert error["security_level"] == SecurityLevel.MEDIUM
    
    # Verify metrics
    metrics = handler.get_metrics_report()
    assert "ErrorCount" in metrics
    assert "ErrorDetectionTime" in metrics
    assert "LoggingLatency" in metrics
    assert "DetectionRate" in metrics
    assert "RecoveryTime" in metrics
    assert "FalsePositiveRate" in metrics
    assert "FalseNegativeRate" in metrics
    assert "ClassificationAccuracy" in metrics
    
    # Verify compliance
    compliance = handler.get_compliance_report()
    assert "ISO27001" in compliance
    assert "GDPR" in compliance
    assert "HIPAA" in compliance 