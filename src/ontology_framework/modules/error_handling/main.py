# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: [current version from guidance.ttl]
# Behavioral-Profile: ClaudeReflector

"""Main error handler module."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import time
from .types import (
    ValidationRuleType,
    ComplianceLevel,
    RiskLevel,
    RuleSeverity, ComplianceRule, ComplianceResult
)
from .validation import ValidationHandler
from .compliance import ComplianceHandler

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Main error handler class."""
    
    def __init__(self):
        """Initialize error handler."""
        self.validation_handler = ValidationHandler()
        self.compliance_handler = ComplianceHandler()
        self.errors: List[Dict[str, Any]] = []
        self.start_time = datetime.utcnow()
    
    def handle_error(self, error: Dict[str, Any]) -> None:
        """Handle an error."""
        error["timestamp"] = datetime.utcnow()
        error["elapsed_time"] = (error["timestamp"] - self.start_time).total_seconds()
        
        logger.error(f"Error occurred: {error}")
        self.errors.append(error)
        
        # Validate error against rules
        validation_result = self.validation_handler.validate(error)
        if not validation_result["is_valid"]:
            logger.warning(f"Error validation failed: {validation_result['message']}")
        
        # Check compliance
        compliance_result = self.compliance_handler.check_compliance(error)
        if not compliance_result.is_compliant:
            logger.warning(f"Compliance check failed: {compliance_result.violations}")
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all errors."""
        return self.errors
    
    def clear_errors(self) -> None:
        """Clear all errors."""
        self.errors = []
        self.start_time = datetime.utcnow()
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        if not self.errors:
            return {
                "total_errors": 0,
                "start_time": self.start_time,
                "end_time": datetime.utcnow(),
                "duration": 0,
                "error_rate": 0
            }
        
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        return {
            "total_errors": len(self.errors),
            "start_time": self.start_time,
            "end_time": end_time,
            "duration": duration,
            "error_rate": len(self.errors) / duration if duration > 0 else 0
        }
    
    def export_error_report(self) -> Dict[str, Any]:
        """Export error report."""
        stats = self.get_error_stats()
        validation_report = self.validation_handler.get_validation_report()
        compliance_report = self.compliance_handler.export_compliance_report()
        
        return {
            "statistics": stats,
            "validation": validation_report,
            "compliance": compliance_report,
            "errors": self.errors
        } 