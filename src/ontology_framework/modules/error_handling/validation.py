"""Validation module for error handling."""

from typing import Dict, Any, List, Optional
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH

# Define validation rule types
class ValidationRule(Enum):
    """Validation rule types."""
    MATRIX = auto()
    ONTOLOGY = auto()
    PATTERN = auto()
    COMPLIANCE = auto()
    PERFORMANCE = auto()
    SENSITIVE_DATA = auto()
    RISK = auto()
    SECURITY = auto()
    RELIABILITY = auto()
    AVAILABILITY = auto()
    SCALABILITY = auto()
    MAINTAINABILITY = auto()
    SEVERITY = auto()
    STEP_ORDER = auto()
    ACCESS_CONTROL = auto()
    ENCRYPTION = auto()
    SPORE = auto()
    SEMANTIC = auto()
    SYNTAX = auto()
    INDIVIDUAL_TYPE = auto()

@dataclass
class ValidationResult:
    """Class representing a validation result."""
    rule: ValidationRule
    is_valid: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class ValidationHandler:
    """Handler class for validation operations."""
    
    def __init__(self):
        """Initialize validation handler."""
        self._validation_history: List[ValidationResult] = []
        self._setup_validation_rules()
    
    def _setup_validation_rules(self):
        """Set up validation rules."""
        self._rules = {
            ValidationRule.MATRIX: self._validate_matrix,
            ValidationRule.ONTOLOGY: self._validate_ontology,
            ValidationRule.PATTERN: self._validate_pattern,
            ValidationRule.COMPLIANCE: self._validate_compliance,
            ValidationRule.PERFORMANCE: self._validate_performance,
            ValidationRule.SENSITIVE_DATA: self._validate_sensitive_data,
            ValidationRule.RISK: self._validate_risk,
            ValidationRule.SECURITY: self._validate_security,
            ValidationRule.RELIABILITY: self._validate_reliability,
            ValidationRule.AVAILABILITY: self._validate_availability,
            ValidationRule.SCALABILITY: self._validate_scalability,
            ValidationRule.MAINTAINABILITY: self._validate_maintainability,
            ValidationRule.SEVERITY: self._validate_severity,
            ValidationRule.STEP_ORDER: self._validate_step_order,
            ValidationRule.ACCESS_CONTROL: self._validate_access_control,
            ValidationRule.ENCRYPTION: self._validate_encryption,
            ValidationRule.SPORE: self._validate_spore,
            ValidationRule.SEMANTIC: self._validate_semantic,
            ValidationRule.SYNTAX: self._validate_syntax,
            ValidationRule.INDIVIDUAL_TYPE: self._validate_individual_type
        }
    
    def validate(self, rule: ValidationRule, data: Dict[str, Any]) -> ValidationResult:
        """Validate data against a rule."""
        if rule not in self._rules:
            raise ValueError(f"Rule {rule} not found")
        
        validator = self._rules[rule]
        result = validator(data)
        self._validation_history.append(result)
        return result
    
    def get_validation_history(self) -> List[ValidationResult]:
        """Get validation history."""
        return self._validation_history
    
    def _validate_matrix(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate matrix data."""
        required_fields = ["matrix_id", "matrix_type", "matrix_level"]
        if not all(field in data for field in required_fields):
            return ValidationResult(
                rule=ValidationRule.MATRIX,
                is_valid=False,
                message="Missing required fields",
                details={"missing_fields": [f for f in required_fields if f not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.MATRIX,
            is_valid=True,
            message="Matrix validation passed"
        )
    
    def _validate_ontology(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate ontology data."""
        if "ontology_id" not in data:
            return ValidationResult(
                rule=ValidationRule.ONTOLOGY,
                is_valid=False,
                message="Missing ontology ID"
            )
        return ValidationResult(
            rule=ValidationRule.ONTOLOGY,
            is_valid=True,
            message="Ontology validation passed"
        )
    
    def _validate_pattern(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate pattern data."""
        required_fields = ["pattern_type", "pattern_elements"]
        if not all(field in data for field in required_fields):
            return ValidationResult(
                rule=ValidationRule.PATTERN,
                is_valid=False,
                message="Missing required fields",
                details={"missing_fields": [f for f in required_fields if f not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.PATTERN,
            is_valid=True,
            message="Pattern validation passed"
        )
    
    def _validate_compliance(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate compliance data."""
        if "compliance_level" not in data:
            return ValidationResult(
                rule=ValidationRule.COMPLIANCE,
                is_valid=False,
                message="Missing compliance level"
            )
        return ValidationResult(
            rule=ValidationRule.COMPLIANCE,
            is_valid=True,
            message="Compliance validation passed"
        )
    
    def _validate_performance(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate performance data."""
        required_metrics = ["response_time", "throughput", "error_rate"]
        if not all(metric in data for metric in required_metrics):
            return ValidationResult(
                rule=ValidationRule.PERFORMANCE,
                is_valid=False,
                message="Missing required metrics",
                details={"missing_metrics": [m for m in required_metrics if m not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.PERFORMANCE,
            is_valid=True,
            message="Performance validation passed"
        )
    
    def _validate_sensitive_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate sensitive data."""
        if "data" not in data:
            return ValidationResult(
                rule=ValidationRule.SENSITIVE_DATA,
                is_valid=False,
                message="Missing data field"
            )
        return ValidationResult(
            rule=ValidationRule.SENSITIVE_DATA,
            is_valid=True,
            message="Sensitive data validation passed"
        )
    
    def _validate_risk(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate risk data."""
        required_fields = ["level", "impact", "probability"]
        if not all(field in data for field in required_fields):
            return ValidationResult(
                rule=ValidationRule.RISK,
                is_valid=False,
                message="Missing required fields",
                details={"missing_fields": [f for f in required_fields if f not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.RISK,
            is_valid=True,
            message="Risk validation passed"
        )
    
    def _validate_security(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate security data."""
        if "security_level" not in data:
            return ValidationResult(
                rule=ValidationRule.SECURITY,
                is_valid=False,
                message="Missing security level"
            )
        return ValidationResult(
            rule=ValidationRule.SECURITY,
            is_valid=True,
            message="Security validation passed"
        )
    
    def _validate_reliability(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate reliability data."""
        required_metrics = ["uptime", "mtbf", "mttr"]
        if not all(metric in data for metric in required_metrics):
            return ValidationResult(
                rule=ValidationRule.RELIABILITY,
                is_valid=False,
                message="Missing required metrics",
                details={"missing_metrics": [m for m in required_metrics if m not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.RELIABILITY,
            is_valid=True,
            message="Reliability validation passed"
        )
    
    def _validate_availability(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate availability data."""
        if "availability_percentage" not in data:
            return ValidationResult(
                rule=ValidationRule.AVAILABILITY,
                is_valid=False,
                message="Missing availability percentage"
            )
        return ValidationResult(
            rule=ValidationRule.AVAILABILITY,
            is_valid=True,
            message="Availability validation passed"
        )
    
    def _validate_scalability(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate scalability data."""
        required_metrics = ["load_capacity", "response_time_under_load"]
        if not all(metric in data for metric in required_metrics):
            return ValidationResult(
                rule=ValidationRule.SCALABILITY,
                is_valid=False,
                message="Missing required metrics",
                details={"missing_metrics": [m for m in required_metrics if m not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.SCALABILITY,
            is_valid=True,
            message="Scalability validation passed"
        )
    
    def _validate_maintainability(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate maintainability data."""
        required_metrics = ["code_coverage", "technical_debt"]
        if not all(metric in data for metric in required_metrics):
            return ValidationResult(
                rule=ValidationRule.MAINTAINABILITY,
                is_valid=False,
                message="Missing required metrics",
                details={"missing_metrics": [m for m in required_metrics if m not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.MAINTAINABILITY,
            is_valid=True,
            message="Maintainability validation passed"
        )
    
    def _validate_severity(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate severity data."""
        if "severity_level" not in data:
            return ValidationResult(
                rule=ValidationRule.SEVERITY,
                is_valid=False,
                message="Missing severity level"
            )
        return ValidationResult(
            rule=ValidationRule.SEVERITY,
            is_valid=True,
            message="Severity validation passed"
        )
    
    def _validate_step_order(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate step order data."""
        required_fields = ["step_id", "order"]
        if not all(field in data for field in required_fields):
            return ValidationResult(
                rule=ValidationRule.STEP_ORDER,
                is_valid=False,
                message="Missing required fields",
                details={"missing_fields": [f for f in required_fields if f not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.STEP_ORDER,
            is_valid=True,
            message="Step order validation passed"
        )
    
    def _validate_access_control(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate access control data."""
        required_fields = ["user_role", "permissions"]
        if not all(field in data for field in required_fields):
            return ValidationResult(
                rule=ValidationRule.ACCESS_CONTROL,
                is_valid=False,
                message="Missing required fields",
                details={"missing_fields": [f for f in required_fields if f not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.ACCESS_CONTROL,
            is_valid=True,
            message="Access control validation passed"
        )
    
    def _validate_encryption(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate encryption data."""
        required_fields = ["algorithm", "key_length"]
        if not all(field in data for field in required_fields):
            return ValidationResult(
                rule=ValidationRule.ENCRYPTION,
                is_valid=False,
                message="Missing required fields",
                details={"missing_fields": [f for f in required_fields if f not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.ENCRYPTION,
            is_valid=True,
            message="Encryption validation passed"
        )
    
    def _validate_spore(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate SPORE data."""
        required_fields = ["pattern_type", "pattern_elements", "constraints"]
        if not all(field in data for field in required_fields):
            return ValidationResult(
                rule=ValidationRule.SPORE,
                is_valid=False,
                message="Missing required fields",
                details={"missing_fields": [f for f in required_fields if f not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.SPORE,
            is_valid=True,
            message="SPORE validation passed"
        )
    
    def _validate_semantic(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate semantic data."""
        required_fields = ["ontology_id", "validation_type", "data_format"]
        if not all(field in data for field in required_fields):
            return ValidationResult(
                rule=ValidationRule.SEMANTIC,
                is_valid=False,
                message="Missing required fields",
                details={"missing_fields": [f for f in required_fields if f not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.SEMANTIC,
            is_valid=True,
            message="Semantic validation passed"
        )
    
    def _validate_syntax(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate syntax data."""
        required_fields = ["code", "language", "version"]
        if not all(field in data for field in required_fields):
            return ValidationResult(
                rule=ValidationRule.SYNTAX,
                is_valid=False,
                message="Missing required fields",
                details={"missing_fields": [f for f in required_fields if f not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.SYNTAX,
            is_valid=True,
            message="Syntax validation passed"
        )
    
    def _validate_individual_type(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate individual type data."""
        required_fields = ["individual_uri", "type_assertions", "property_values"]
        if not all(field in data for field in required_fields):
            return ValidationResult(
                rule=ValidationRule.INDIVIDUAL_TYPE,
                is_valid=False,
                message="Missing required fields",
                details={"missing_fields": [f for f in required_fields if f not in data]}
            )
        return ValidationResult(
            rule=ValidationRule.INDIVIDUAL_TYPE,
            is_valid=True,
            message="Individual type validation passed"
        )

__all__ = ['ValidationHandler'] 