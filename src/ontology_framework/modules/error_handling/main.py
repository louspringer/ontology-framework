from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import time
from .types import (
    ErrorStep,
    ErrorSeverity,
    SecurityLevel,
    RiskLevel,
    ValidationRule,
    ValidationRuleType
)
from .validation import ValidationHandler
from .security import SecurityHandler
from .metrics import MetricsHandler
from .compliance import ComplianceHandler
from .rdf import RDFHandler

class ErrorHandler:
    """Class for handling runtime errors and validation."""
    
    VERSION = "1.0.0"
    
    def __init__(self) -> None:
        """Initialize error handler with default error types and handling steps."""
        self._errors: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        self.validation_handler = ValidationHandler()
        self.security_handler = SecurityHandler()
        self.metrics_handler = MetricsHandler()
        self.compliance_handler = ComplianceHandler()
        self.rdf_handler = RDFHandler()
        self.current_step = ErrorStep.IDENTIFICATION

    def validate_security(self, rule: ValidationRuleType, data: Any) -> bool:
        """Validate security-related rules."""
        result = self.security_handler.validate(rule, data)
        if not result.is_valid:
            self.logger.error(f"Security validation failed: {result.message}")
            if result.details:
                self.logger.error(f"Details: {result.details}")
        return result.is_valid
        
    def handle_error(self, error_type: str, message: str, **kwargs) -> Dict[str, Any]:
        """Handle an error with appropriate validation and logging."""
        error = {
            'type': error_type,
            'message': message,
            'timestamp': datetime.utcnow(),
            'step': self.current_step,
            **kwargs
        }
        
        # Validate security if applicable
        if error_type in ['security_error', 'compliance_error']:
            security_data = {
                'encrypted': kwargs.get('encrypted', False),
                'access_control': kwargs.get('access_control', SecurityLevel.CONFIDENTIAL),
                'retention_period': kwargs.get('retention_period', 'P1Y')
            }
            if not self.validate_security(ValidationRuleType.SENSITIVE_DATA, security_data):
                error['security_validation_failed'] = True
                
        self._errors.append(error)
        self.metrics_handler.track_error(error)
        return error
        
    def get_current_step(self) -> ErrorStep:
        """Get the current error handling step."""
        return self.current_step
        
    def set_current_step(self, step: ErrorStep) -> None:
        """Set the current error handling step."""
        self.current_step = step

    def add_error(self, error_type: str, message: str, severity: str = "MEDIUM") -> None:
        """Add an error to the error handler."""
        start_time = time.time()
        
        error: Dict[str, Any] = {
            'type': error_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'context': '',
            'documentation': '',
            'validation_results': []
        }
        
        # Validate error
        if not self.validation_handler.validate(ValidationRule(
            description="Validate error severity",
            severity="HIGH",
            message_template="Invalid error severity: {message}",
            rule_type="severity"
        ), severity):
            self.logger.error(f"Invalid error severity: {severity}")
            return
            
        self._errors.append(error)
        
        # Update metrics
        detection_time = time.time() - start_time
        self.metrics_handler.update_metrics(error_type, detection_time)
        self.metrics_handler.update_error_matrix(error_type, True)
        self.metrics_handler.calculate_derived_metrics()
        
        # Add to RDF graph
        self.rdf_handler.add_error(error)
        
        self.logger.info(f"Error added: {message} [Type: {error_type}, Severity: {severity}]")

    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all errors."""
        return self._errors

    def get_metrics_report(self) -> Dict[str, Dict[str, Any]]:
        """Get current metrics with thresholds."""
        report = self.metrics_handler.get_metrics_report()
        return {
            "metrics": report["metrics"],
            "thresholds": report["thresholds"],
            "timestamp": report["timestamp"]
        }

    def get_compliance_report(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed compliance report."""
        return self.compliance_handler.get_compliance_report()

    def to_rdf(self) -> str:
        """Convert error handler state to RDF graph."""
        return str(self.rdf_handler.serialize()) 