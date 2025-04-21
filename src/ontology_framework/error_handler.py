"""
Error handling module for the ontology framework.
"""

import logging
from typing import List, Dict, Any, Optional, Set, Union, Callable
from datetime import datetime
from .ontology_types import (
    ErrorType, ErrorSeverity, ErrorStep, ValidationRule, 
    SecurityLevel, ComplianceLevel, RiskLevel, PerformanceMetric
)
import time
from collections import Counter

class ErrorHandler:
    """Class for handling and tracking errors in the ontology framework."""

    # Error type hierarchy
    ERROR_HIERARCHY = {
        ErrorType.VALIDATION: ErrorType.RUNTIME,
        ErrorType.CONFIGURATION: ErrorType.RUNTIME,
        ErrorType.NETWORK: ErrorType.RUNTIME,
        ErrorType.DATABASE: ErrorType.RUNTIME,
        ErrorType.FILE_SYSTEM: ErrorType.RUNTIME,
        ErrorType.MEMORY: ErrorType.RUNTIME,
        ErrorType.CPU: ErrorType.RUNTIME,
        ErrorType.DISK: ErrorType.RUNTIME,
        ErrorType.API: ErrorType.RUNTIME,
        ErrorType.AUTHENTICATION: ErrorType.SECURITY,
        ErrorType.AUTHORIZATION: ErrorType.SECURITY,
        ErrorType.COMPLIANCE: ErrorType.SECURITY,
        ErrorType.SECURITY: ErrorType.RUNTIME,
        ErrorType.PERFORMANCE: ErrorType.RUNTIME,
        ErrorType.SCALABILITY: ErrorType.RUNTIME,
        ErrorType.AVAILABILITY: ErrorType.RUNTIME,
        ErrorType.RELIABILITY: ErrorType.RUNTIME,
        ErrorType.MAINTAINABILITY: ErrorType.RUNTIME,
        ErrorType.DATA_LOSS: ErrorType.RUNTIME
    }

    # Step ordering
    STEP_ORDER = {
        ErrorStep.IDENTIFICATION: 1,
        ErrorStep.ANALYSIS: 2,
        ErrorStep.RECOVERY: 3,
        ErrorStep.PREVENTION: 4,
        ErrorStep.MONITORING: 5,
        ErrorStep.REPORTING: 6,
        ErrorStep.DOCUMENTATION: 7,
        ErrorStep.REVIEW: 8,
        ErrorStep.CLOSURE: 9
    }

    def __init__(self) -> None:
        """Initialize the error handler."""
        self.errors: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        self.validation_rules: Dict[ValidationRule, Callable[[Any], bool]] = {
            ValidationRule.SENSITIVE_DATA: self._validate_sensitive_data,
            ValidationRule.RISK: self._validate_risk,
            ValidationRule.MATRIX: self._validate_matrix,
            ValidationRule.COMPLIANCE: self._validate_compliance,
            ValidationRule.SECURITY: self._validate_security,
            ValidationRule.PERFORMANCE: self._validate_performance,
            ValidationRule.RELIABILITY: self._validate_reliability,
            ValidationRule.AVAILABILITY: self._validate_availability,
            ValidationRule.SCALABILITY: self._validate_scalability,
            ValidationRule.MAINTAINABILITY: self._validate_maintainability,
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

    def add_error(self, error_type: ErrorType, message: str, severity: ErrorSeverity, 
                 step: Optional[ErrorStep] = None, risk_level: Optional[RiskLevel] = None,
                 security_level: Optional[SecurityLevel] = None) -> bool:
        """Add an error to the error handler."""
        start_time = time.time()
        
        error: Dict[str, Any] = {
            "type": error_type,
            "parent_type": self.ERROR_HIERARCHY.get(error_type),
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "step": step or self.current_step,
            "risk_level": risk_level or RiskLevel.HIGH if severity == ErrorSeverity.CRITICAL else RiskLevel.MEDIUM,
            "security_level": security_level or SecurityLevel.MEDIUM,
            "prevention_measures": [],
            "recovery_strategies": [],
        }
        
        # Validate error
        if not self.validate(ValidationRule.SEVERITY, severity):
            self.logger.error(f"Invalid error severity: {severity}")
            return False
            
        if not self.validate(ValidationRule.STEP_ORDER, step):
            self.logger.error(f"Invalid step order: {step}")
            return False
            
        if not self.validate(ValidationRule.SECURITY, security_level):
            self.logger.error(f"Invalid security level: {security_level}")
            return False
            
        if not self.validate(ValidationRule.PERFORMANCE, error):
            self.logger.error(f"Performance validation failed")
            return False
            
        if not self.validate(ValidationRule.RELIABILITY, error):
            self.logger.error(f"Reliability validation failed")
            return False
            
        if not self.validate(ValidationRule.AVAILABILITY, error):
            self.logger.error(f"Availability validation failed")
            return False
            
        if not self.validate(ValidationRule.SCALABILITY, error):
            self.logger.error(f"Scalability validation failed")
            return False
            
        if not self.validate(ValidationRule.MAINTAINABILITY, error):
            self.logger.error(f"Maintainability validation failed")
            return False
            
        self.errors.append(error)
        
        # Update metrics
        self.metrics["ErrorCount"]["current"] += 1
        detection_time = time.time() - start_time
        self.metrics["ErrorDetectionTime"]["current"] = max(self.metrics["ErrorDetectionTime"]["current"], detection_time)
        self.metrics["LoggingLatency"]["current"] = max(self.metrics["LoggingLatency"]["current"], detection_time)
        
        # Update error matrix
        if error_type in [ErrorType.VALIDATION, ErrorType.RUNTIME]:
            self.error_matrix["true_positive"] += 1
        else:
            self.error_matrix["false_positive"] += 1

        # Calculate derived metrics
        total_errors = self.error_matrix["true_positive"] + self.error_matrix["false_positive"]
        if total_errors > 0:
            self.metrics["DetectionRate"]["current"] = self.error_matrix["true_positive"] / total_errors
            self.metrics["FalsePositiveRate"]["current"] = self.error_matrix["false_positive"] / total_errors
            self.metrics["ClassificationAccuracy"]["current"] = (
                self.error_matrix["true_positive"] + self.error_matrix["true_negative"]
            ) / total_errors

        # Log error
        self.logger.info(f"Error added: {message} [Type: {error_type.value}, Severity: {severity.value}]")
        return True

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

    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all errors."""
        return self.errors

    def clear_errors(self) -> None:
        """Clear all errors."""
        self.errors = []

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[Dict[str, Any]]:
        """
        Get errors filtered by severity.
        
        Args:
            severity: Severity level to filter by
            
        Returns:
            List of errors with the specified severity
        """
        return [error for error in self.errors if error["severity"] == severity]

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
            self.add_error(
                ErrorType.VALIDATION,
                f"Unknown validation rule: {rule}",
                ErrorSeverity.CRITICAL
            )
            return False
        return bool(self.validation_rules[rule](data))

    def _validate_matrix(self, data: Any) -> bool:
        """Validate matrix data."""
        return isinstance(data, dict) and "matrix" in data and isinstance(data["matrix"], list)

    def _validate_risk(self, data: Any) -> bool:
        """Validate risk data."""
        return isinstance(data, dict) and "risk_level" in data and isinstance(data["risk_level"], RiskLevel)

    def _validate_sensitive_data(self, data: Any) -> bool:
        """Validate sensitive data."""
        return isinstance(data, dict) and "sensitive" in data and isinstance(data["sensitive"], bool)

    def _validate_compliance(self, data: Any) -> bool:
        """Validate compliance data."""
        if not isinstance(data, dict):
            return False
        if "standard" not in data or "requirement" not in data or "status" not in data:
            return False
        return (data["standard"] in self.compliance and 
                data["requirement"] in self.compliance[data["standard"]]["requirements"] and 
                isinstance(data["status"], bool))

    def _validate_severity(self, severity: ErrorSeverity) -> bool:
        """Validate error severity."""
        return isinstance(severity, ErrorSeverity)

    def _validate_step_order(self, step: ErrorStep) -> bool:
        """Validate step order."""
        return isinstance(step, ErrorStep)

    def _validate_security(self, security_level: SecurityLevel) -> bool:
        """Validate security level."""
        return isinstance(security_level, SecurityLevel)

    def _validate_performance(self, error: Dict[str, Any]) -> bool:
        """Validate performance metrics."""
        return isinstance(error, dict) and "type" in error and isinstance(error["type"], ErrorType)

    def _validate_reliability(self, error: Dict[str, Any]) -> bool:
        """Validate reliability metrics."""
        return isinstance(error, dict) and "type" in error and isinstance(error["type"], ErrorType)

    def _validate_availability(self, error: Dict[str, Any]) -> bool:
        """Validate availability metrics."""
        return isinstance(error, dict) and "type" in error and isinstance(error["type"], ErrorType)

    def _validate_scalability(self, error: Dict[str, Any]) -> bool:
        """Validate scalability metrics."""
        return isinstance(error, dict) and "type" in error and isinstance(error["type"], ErrorType)

    def _validate_maintainability(self, error: Dict[str, Any]) -> bool:
        """Validate maintainability metrics."""
        return isinstance(error, dict) and "type" in error and isinstance(error["type"], ErrorType)

    def get_current_step(self) -> ErrorStep:
        """Get the current error handling step."""
        return self.current_step

    def set_current_step(self, step: ErrorStep) -> None:
        """
        Set the current error handling step.
        
        Args:
            step: New error handling step
        """
        if step in self.STEP_ORDER:
            current_order = self.STEP_ORDER[self.current_step]
            new_order = self.STEP_ORDER[step]
            if new_order < current_order:
                self.logger.warning(f"Moving back in error handling steps: {self.current_step} -> {step}")
        self.current_step = step

    def get_error_types(self) -> Dict[ErrorType, str]:
        """Get all error types."""
        return self.error_types

    def get_validation_rules(self) -> List[ValidationRule]:
        """Get all validation rules."""
        return list(self.validation_rules.keys())

    def update_compliance(self, standard: str, requirement: str, status: bool) -> None:
        """Update compliance status for a specific requirement."""
        if standard in self.compliance and requirement in self.compliance[standard]["requirements"]:
            self.compliance[standard]["requirements"][requirement] = status
            self._update_compliance_level(standard)
            self.logger.info(f"Updated {standard} {requirement} compliance to {status}")
        else:
            self.logger.error(f"Unknown compliance standard or requirement: {standard}.{requirement}")

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

    def get_compliance_report(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed compliance report."""
        report: Dict[str, Dict[str, Any]] = {}
        for standard, data in self.compliance.items():
            report[standard] = {
                "level": data["level"],
                "requirements": data["requirements"],
                "status": "COMPLIANT" if data["level"] == ComplianceLevel.FULL else "NON_COMPLIANT"
            }
        return report

    def check_compliance(self, standard: str) -> bool:
        """Check if a specific standard is fully compliant."""
        return (standard in self.compliance and 
                self.compliance[standard]["level"] == ComplianceLevel.FULL)

    def get_metrics_report(self) -> Dict[str, Dict[str, Any]]:
        """Get current metrics with thresholds."""
        report = {}
        for metric, data in self.metrics.items():
            status = "OK" if data["current"] <= data["threshold"] else "WARNING"
            report[metric] = {
                "current": data["current"],
                "threshold": data["threshold"],
                "status": status
            }
        return report

    def check_metrics_thresholds(self) -> bool:
        """Check if all metrics are within thresholds."""
        return all(data["current"] <= data["threshold"] for data in self.metrics.values())

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error handling state."""
        return {
            "total_errors": len(self.errors),
            "errors_by_type": Counter(error["type"] for error in self.errors),
            "errors_by_severity": Counter(error["severity"] for error in self.errors),
            "current_step": self.current_step.value,
            "metrics_report": self.get_metrics_report(),
            "compliance_report": self.get_compliance_report()
        } 