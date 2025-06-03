"""
Error handling module for the ontology framework.
"""

import logging
from typing import List, Dict, Any, Optional, Set, Union, Callable
from datetime import datetime
from .ontology_types import (
    ErrorType, ErrorSeverity, ErrorStep, ValidationRule, 
    SecurityLevel, ComplianceLevel, RiskLevel, PerformanceMetric, ValidationRuleType, ErrorResult
)
from .error import Error
import time
from collections import Counter
import re

class ErrorHandler:
    """Class for handling and tracking errors in the ontology framework."""

    # Error type hierarchy
    ERROR_HIERARCHY = {
        ErrorType.VALIDATION: ErrorType.RUNTIME, ErrorType.CONFIGURATION: ErrorType.RUNTIME,
        ErrorType.NETWORK: ErrorType.RUNTIME,
        ErrorType.DATABASE: ErrorType.RUNTIME,
        ErrorType.FILE_SYSTEM: ErrorType.RUNTIME,
        ErrorType.MEMORY: ErrorType.RUNTIME,
        ErrorType.CPU: ErrorType.RUNTIME,
        ErrorType.DISK: ErrorType.RUNTIME,
        ErrorType.API: ErrorType.RUNTIME,
        ErrorType.AUTHENTICATION: ErrorType.MATRIX,
        ErrorType.AUTHORIZATION: ErrorType.MATRIX,
        ErrorType.COMPLIANCE: ErrorType.MATRIX,
        ErrorType.MATRIX: ErrorType.RUNTIME,
        ErrorType.PERFORMANCE: ErrorType.RUNTIME,
        ErrorType.SCALABILITY: ErrorType.RUNTIME,
        ErrorType.AVAILABILITY: ErrorType.RUNTIME,
        ErrorType.RELIABILITY: ErrorType.RUNTIME,
        ErrorType.MAINTAINABILITY: ErrorType.RUNTIME,
        ErrorType.DATA_LOSS: ErrorType.RUNTIME
    }

    # Step ordering
    STEP_ORDER = {
        ErrorStep.IDENTIFICATION: 1, ErrorStep.ANALYSIS: 2,
        ErrorStep.VALIDATION: 3,
        ErrorStep.PREVENTION: 4,
        ErrorStep.RECOVERY: 5,
        ErrorStep.MONITORING: 6,
        ErrorStep.REPORTING: 7,
        ErrorStep.DOCUMENTATION: 8, ErrorStep.REVIEW: 9, ErrorStep.CLOSURE: 10
    }

    def __init__(self) -> None:
        """Initialize the error handler."""
        self.errors: List[Error] = []
        self.logger = logging.getLogger(__name__)
        self.validation_rules: Dict[ValidationRule, Callable[[Any], bool]] = {
            ValidationRule.SENSITIVE_DATA: self._validate_sensitive_data,
            ValidationRule.RISK: self.validate_risk,
            ValidationRule.MATRIX: self.validate_matrix,
            ValidationRule.COMPLIANCE: self._validate_compliance,
            ValidationRule.PERFORMANCE: self.validate_performance,
            ValidationRule.RELIABILITY: self._validate_reliability,
            ValidationRule.AVAILABILITY: self._validate_availability,
            ValidationRule.SCALABILITY: self.validate_scalability,
            ValidationRule.MAINTAINABILITY: self.validate_maintainability,
            ValidationRule.SEVERITY: self._validate_severity,
            ValidationRule.STEP_ORDER: self._validate_step_order
        }
        self.current_step = ErrorStep.IDENTIFICATION
        self.error_types = {error_type: error_type.value for error_type in ErrorType}

        # Track prevention measures and recovery strategies
        self.prevention_measures: Dict[str, bool] = {
            "ErrorBoundary": False,
            "InputValidation": False,
            "AutomaticRetry": False,
            "Checkpoint": False,
            "CircuitBreaker": False,
            "RateLimiting": False,
            "ResourceQuotas": False,
            "AccessControl": False
        }
        self.recovery_strategies: Dict[str, bool] = {
            "AutomaticFailover": False,
            "DataReplication": False,
            "StateRecovery": False,
            "ServiceRestart": False
        }

        # Initialize metrics
        self.metrics: Dict[str, Dict[str, Union[int, float]]] = {
            "ErrorCount": {"current": 0, "threshold": 100},
            "ErrorDetectionTime": {"current": 0, "threshold": 300},
            "LoggingLatency": {"current": 0, "threshold": 1},
            "DetectionRate": {"current": 0, "threshold": 0.95},
            "RecoveryTime": {"current": 0, "threshold": 60},
            "FalsePositiveRate": {"current": 0, "threshold": 0.05},
            "FalseNegativeRate": {"current": 0, "threshold": 0.05},
            "ClassificationAccuracy": {"current": 0, "threshold": 0.98}
        }

        # Initialize compliance tracking
        self.compliance: Dict[str, Dict[str, Any]] = {
            "ISO27001": {
                "level": ComplianceLevel.NOT_STARTED,
                "requirements": {
                    "access_control": False,
                    "encryption": False,
                    "audit_logging": False,
                    "incident_management": False,
                    "risk_assessment": False
                }
            },
            "GDPR": {
                "level": ComplianceLevel.NOT_STARTED,
                "requirements": {
                    "data_protection": False,
                    "consent_management": False,
                    "data_portability": False,
                    "right_to_be_forgotten": False,
                    "privacy_by_design": False
                }
            },
            "HIPAA": {
                "level": ComplianceLevel.NOT_STARTED,
                "requirements": {
                    "phi_protection": False,
                    "access_controls": False,
                    "audit_controls": False,
                    "integrity_controls": False,
                    "transmission_security": False
                }
            }
        }

        self.error_matrix: Dict[str, int] = {
            "true_positive": 0,
            "true_negative": 0,
            "false_positive": 0,
            "false_negative": 0
        }

    def add_error(self, error: Error) -> None:
        """Add an error to the handler."""
        if not isinstance(error, Error):
            raise ValueError("Error must be an instance of Error class")
        self.errors.append(error)
        self.logger.debug(f"Added error: {error}")

    def add_prevention_measure(self, measure: str) -> None:
        """Add a prevention measure."""
        self.prevention_measures[measure] = True

    def add_recovery_strategy(self, strategy: str) -> None:
        """Add a recovery strategy."""
        self.recovery_strategies[strategy] = True

    def get_prevention_measures(self) -> Set[str]:
        """Get all prevention measures."""
        return {measure for measure, active in self.prevention_measures.items() if active}

    def get_recovery_strategies(self) -> Set[str]:
        """Get all recovery strategies."""
        return {strategy for strategy, active in self.recovery_strategies.items() if active}

    def get_errors(self) -> List[Error]:
        """Get all errors."""
        return self.errors

    def clear_errors(self) -> None:
        """Clear all errors from the handler."""
        self.errors.clear()
        self.logger.debug("Cleared all errors")

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[Error]:
        """
        Get errors filtered by severity.
        
        Args:
            severity: Severity level to filter by
            Returns:
            List of errors with the specified severity
        """
        return [error for error in self.errors if error.severity == severity]

    def validate(self, rule: ValidationRule, data: Any) -> bool:
        """
        Validate data using the specified rule.
        
        Args:
            rule: Validation rule to apply
            data: Data to validate
            Returns:
            True if validation passes, False otherwise
        """
        if rule not in self.validation_rules:
            error = Error(
                error_type=ErrorType.VALIDATION,
                message=f"Unknown validation rule: {rule}",
                severity=ErrorSeverity.CRITICAL,
                step=ErrorStep.VALIDATION
            )
            self.add_error(error)
            return False
        return bool(self.validation_rules[rule](data))

    def validate_risk(self, data: Any) -> bool:
        """
        Validate risk data.
        
        Args:
            data: Data to validate
            Returns:
            True if validation passes, False otherwise
        """
        try:
            if not isinstance(data, dict):
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="Risk data must be a dictionary",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            if "risk_level" not in data:
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="Risk data must contain 'risk_level' key",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            risk_level = data["risk_level"]
            if not isinstance(risk_level, RiskLevel):
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="Risk level must be a RiskLevel enum value",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            return True
        except Exception as e:
            error = Error(
                error_type=ErrorType.VALIDATION,
                message=f"Risk validation failed: {str(e)}",
                severity=ErrorSeverity.HIGH,
                step=ErrorStep.VALIDATION
            )
            self.add_error(error)
            return False

    def validate_matrix(self, data: Any) -> bool:
        """
        Validate matrix data.
        
        Args:
            data: Data to validate
            Returns:
            True if validation passes, False otherwise
        """
        try:
            if not isinstance(data, dict):
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="Matrix data must be a dictionary",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            if "matrix" not in data:
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="Matrix data must contain 'matrix' key",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            matrix = data["matrix"]
            if not isinstance(matrix, list) or not all(isinstance(row, list) for row in matrix):
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="Matrix must be a list of lists",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            return True
        except Exception as e:
            error = Error(
                error_type=ErrorType.VALIDATION,
                message=f"Matrix validation failed: {str(e)}",
                severity=ErrorSeverity.HIGH,
                step=ErrorStep.VALIDATION
            )
            self.add_error(error)
            return False

    def _validate_sensitive_data(self, data: Any) -> bool:
        """
        Validate sensitive data.
        
        Args:
            data: Data to validate
            Returns:
            True if validation passes, False otherwise
        """
        try:
            if not isinstance(data, dict):
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="Sensitive data must be a dictionary",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            if "encrypted" not in data or "access_control" not in data:
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="Sensitive data must contain 'encrypted' and 'access_control' keys",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            if not isinstance(data["encrypted"], bool):
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="'encrypted' field must be a boolean",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            if not isinstance(data["access_control"], SecurityLevel):
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="'access_control' field must be a SecurityLevel enum value",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            return True
        except Exception as e:
            error = Error(
                error_type=ErrorType.VALIDATION,
                message=f"Sensitive data validation failed: {str(e)}",
                severity=ErrorSeverity.HIGH,
                step=ErrorStep.VALIDATION
            )
            self.add_error(error)
            return False

    def _validate_compliance(self, data: Any) -> bool:
        """
        Validate compliance data.
        
        Args:
            data: Data to validate
            Returns:
            True if validation passes, False otherwise
        """
        try:
            if not isinstance(data, dict):
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="Compliance data must be a dictionary",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            if "standard" not in data or "compliance_level" not in data:
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="Compliance data must contain 'standard' and 'compliance_level' keys",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            if not isinstance(data["standard"], str):
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="'standard' field must be a string",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            if not isinstance(data["compliance_level"], ComplianceLevel):
                error = Error(
                    error_type=ErrorType.VALIDATION,
                    message="'compliance_level' field must be a ComplianceLevel enum value",
                    severity=ErrorSeverity.HIGH,
                    step=ErrorStep.VALIDATION
                )
                self.add_error(error)
                return False

            return True
        except Exception as e:
            error = Error(
                error_type=ErrorType.VALIDATION,
                message=f"Compliance validation failed: {str(e)}",
                severity=ErrorSeverity.HIGH,
                step=ErrorStep.VALIDATION
            )
            self.add_error(error)
            return False

    def _validate_severity(self, severity: ErrorSeverity) -> bool:
        """Validate error severity."""
        return isinstance(severity, ErrorSeverity)

    def _validate_step_order(self, step: ErrorStep) -> bool:
        """Validate step order."""
        return isinstance(step, ErrorStep)

    def validate_performance(self, data: Any) -> bool:
        """Validate performance data."""
        try:
            if not isinstance(data, dict):
                return False
                
            # Check for required fields
            required_fields = ["type", "severity", "message", "metrics"]
            if not all(field in data for field in required_fields):
                return False
                
            # Validate metrics
            metrics = data["metrics"]
            if not isinstance(metrics, dict):
                return False
                
            # Check for required metrics
            required_metrics = ["response_time", "throughput", "error_rate"]
            if not all(metric in metrics for metric in required_metrics):
                return False
                
            # Validate metric values for metric in required_metrics:
            for metric in required_metrics:
                if not isinstance(metrics[metric], (int, float)) or metrics[metric] < 0:
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Performance validation failed: {str(e)}")
            return False

    def _validate_reliability(self, data: Any) -> bool:
        """Validate reliability data."""
        try:
            if not isinstance(data, dict):
                return False
                
            # Check for required fields
            required_fields = ["type", "severity", "message", "reliability_metrics"]
            if not all(field in data for field in required_fields):
                return False
                
            # Validate reliability metrics
            metrics = data["reliability_metrics"]
            if not isinstance(metrics, dict):
                return False
                
            # Check for required metrics
            required_metrics = ["mtbf", "mttr", "availability"]
            if not all(metric in metrics for metric in required_metrics):
                return False
                
            # Validate metric values for metric in required_metrics:
            for metric in required_metrics:
                if not isinstance(metrics[metric], (int, float)) or metrics[metric] < 0:
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Reliability validation failed: {str(e)}")
            return False

    def _validate_availability(self, data: Any) -> bool:
        """Validate availability data."""
        try:
            if not isinstance(data, dict):
                return False
                
            # Check for required fields
            required_fields = ["type", "severity", "message", "availability_metrics"]
            if not all(field in data for field in required_fields):
                return False
                
            # Validate availability metrics
            metrics = data["availability_metrics"]
            if not isinstance(metrics, dict):
                return False
                
            # Check for required metrics
            required_metrics = ["uptime", "downtime", "availability_percentage"]
            if not all(metric in metrics for metric in required_metrics):
                return False
                
            # Validate metric values for metric in required_metrics:
            for metric in required_metrics:
                if not isinstance(metrics[metric], (int, float)) or metrics[metric] < 0:
                    return False
                    
            # Validate availability percentage
            if not 0 <= metrics["availability_percentage"] <= 100:
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Availability validation failed: {str(e)}")
            return False

    def validate_scalability(self, data: Any) -> bool:
        """Validate scalability data."""
        try:
            if not isinstance(data, dict):
                return False
                
            # Check for required fields
            required_fields = ["type", "severity", "message", "scalability_metrics"]
            if not all(field in data for field in required_fields):
                return False
                
            # Validate scalability metrics
            metrics = data["scalability_metrics"]
            if not isinstance(metrics, dict):
                return False
                
            # Check for required metrics
            required_metrics = ["throughput", "latency", "resource_utilization"]
            if not all(metric in metrics for metric in required_metrics):
                return False
                
            # Validate metric values for metric in required_metrics:
            for metric in required_metrics:
                if not isinstance(metrics[metric], (int, float)) or metrics[metric] < 0:
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Scalability validation failed: {str(e)}")
            return False

    def validate_maintainability(self, data: Any) -> bool:
        """Validate maintainability data."""
        try:
            if not isinstance(data, dict):
                return False
                
            # Check for required fields
            required_fields = ["type", "severity", "message", "maintainability_metrics"]
            if not all(field in data for field in required_fields):
                return False
                
            # Validate maintainability metrics
            metrics = data["maintainability_metrics"]
            if not isinstance(metrics, dict):
                return False
                
            # Check for required metrics
            required_metrics = ["complexity", "test_coverage", "documentation_score"]
            if not all(metric in metrics for metric in required_metrics):
                return False
                
            # Validate metric values for metric in required_metrics:
            for metric in required_metrics:
                if not isinstance(metrics[metric], (int, float)) or metrics[metric] < 0:
                    return False
                    
            # Validate score ranges
            if not 0 <= metrics["test_coverage"] <= 100:
                return False
            if not 0 <= metrics["documentation_score"] <= 100:
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Maintainability validation failed: {str(e)}")
            return False

    def get_current_step(self) -> ErrorStep:
        """Get the current error handling step."""
        return self.current_step

    def set_current_step(self, step: ErrorStep) -> None:
        """Set the current error handling step."""
        if step not in self.STEP_ORDER:
            raise ValueError(f"Invalid step: {step}")
        
        current_order = self.STEP_ORDER[self.current_step]
        new_order = self.STEP_ORDER[step]
        
        if new_order < current_order:
            self.logger.warning(f"Moving back in error handling steps: {self.current_step} -> {step}")
        
        self.current_step = step
        self.logger.debug(f"Current step set to: {step}")

    def get_error_types(self) -> Dict[ErrorType, str]:
        """Get all error types."""
        return self.error_types

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get all validation rules."""
        return list(self.validation_rules.keys())

    def update_compliance(self, standard: str, status: str) -> None:
        """Update compliance status for a standard."""
        self.compliance[standard] = status
        self.logger.debug(f"Updated compliance for {standard} to {status}")

    def _update_compliance_level(self, standard: str) -> None:
        """Update overall compliance level based on requirements status."""
        if standard in self.compliance:
            requirements = self.compliance[standard]["requirements"]
            if all(requirements.values()):
                self.compliance[standard]["level"] = ComplianceLevel.FULL
            elif any(requirements.values()):
                self.compliance[standard]["level"] = ComplianceLevel.PARTIAL
            else:
                self.compliance[standard]["level"] = ComplianceLevel.NOT_STARTED

    def get_compliance_report(self) -> Dict[str, str]:
        """Get a report of compliance status for each standard."""
        return {standard: level for standard, level in self.compliance.items()}

    def check_compliance(self, standard: str, level: str) -> bool:
        """
        Check if a specific standard is at the specified compliance level.
        
        Args:
            standard: The compliance standard to check
            level: The expected compliance level
            
        Returns:
            True if the standard is at the specified level, False otherwise
        """
        if standard not in self.compliance:
            return False
        return self.compliance[standard] == level

    def get_metrics_report(self) -> Dict[str, Dict[str, float]]:
        """Get a report of current metrics and their thresholds."""
        return {
            metric: {
                "current": value,
                "threshold": self.metrics[metric]
            }
            for metric, value in self.metrics.items()
        }

    def check_metrics_thresholds(self, metrics: Dict[str, float], thresholds: Dict[str, float]) -> bool:
        """
        Check if metrics are within specified thresholds.
        
        Args:
            metrics: Dictionary of metric names and their values
            thresholds: Dictionary of metric names and their threshold values
            
        Returns:
            bool: True if all metrics are within thresholds, False otherwise
        """
        for metric_name, value in metrics.items():
            if metric_name not in thresholds:
                self.logger.warning(f"No threshold defined for metric: {metric_name}")
                continue
            if value > thresholds[metric_name]:
                return False
                
        return True

    def get_error_summary(self) -> Dict[str, Union[int, Dict[str, int]]]:
        """Get a summary of error counts by severity and type."""
        error_types_count = {}
        severity_levels = {
            "high": len([e for e in self.errors if e.severity == ErrorSeverity.HIGH]),
            "medium": len([e for e in self.errors if e.severity == ErrorSeverity.MEDIUM]),
            "low": len([e for e in self.errors if e.severity == ErrorSeverity.LOW])
        }
        
        for error in self.errors:
            error_type = error.error_type.value.lower()
            error_types_count[error_type] = error_types_count.get(error_type, 0) + 1
        summary = {
            "total_errors": len(self.errors),
            "error_types": error_types_count,
            "severity_levels": severity_levels
        }
        return summary

    def validate_security(self, data: Any) -> bool:
        """Validate security data."""
        try:
            if not isinstance(data, dict):
                return False
                
            # Check for required fields
            required_fields = ["type", "severity", "message", "security_level"]
            if not all(field in data for field in required_fields):
                return False
                
            # Validate security level
            if not isinstance(data["security_level"], str):
                return False
                
            # Check for valid security levels
            valid_levels = ["low", "medium", "high", "critical"]
            if data["security_level"].lower() not in valid_levels:
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Security validation failed: {str(e)}")
            return False 