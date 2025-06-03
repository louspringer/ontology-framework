from typing import Dict, Any, List, Optional
from .types import ValidationRule, ErrorType, ErrorSeverity, SecurityLevel
from .validation import ValidationModule

class ErrorHandler:
    """Error handler class for managing validation and error handling."""

    def __init__(self):
        """Initialize error handler."""
        self.validation_rules = {
            ValidationRule.MATRIX: {
                "required_fields": ["matrix_id", "matrix_type", "matrix_level"],
                "field_types": {
                    "matrix_id": str,
                    "matrix_type": str,
                    "matrix_level": str
                },
                "constraints": {
                    "matrix_id": r"^[A-Za-z0-9_-]+$",
                    "matrix_type": ["access", "risk", "compliance"],
                    "matrix_level": ["low", "medium", "high", "critical"]
                }
            },
            ValidationRule.ONTOLOGY: {
                "required_fields": ["ontology_id", "ontology_type"],
                "field_types": {
                    "ontology_id": str,
                    "ontology_type": str
                },
                "constraints": {
                    "ontology_id": r"^[A-Za-z0-9_-]+$",
                    "ontology_type": ["owl", "rdfs", "skos"]
                }
            },
            ValidationRule.PATTERN: {
                "required_fields": ["pattern_id", "pattern_type"],
                "field_types": {
                    "pattern_id": str,
                    "pattern_type": str
                },
                "constraints": {
                    "pattern_id": r"^[A-Za-z0-9_-]+$",
                    "pattern_type": ["structural", "behavioral", "creational"]
                }
            }
        }

        self.error_hierarchy = {
            ErrorType.MATRIX: [
                ErrorSeverity.CRITICAL,
                ErrorSeverity.HIGH,
                ErrorSeverity.MEDIUM,
                ErrorSeverity.LOW
            ],
            ErrorType.VALIDATION: [
                ErrorSeverity.HIGH,
                ErrorSeverity.MEDIUM,
                ErrorSeverity.LOW
            ],
            ErrorType.RUNTIME: [
                ErrorSeverity.MEDIUM,
                ErrorSeverity.LOW
            ]
        }

        self.step_ordering = {
            "matrix": 1,
            "ontology": 2,
            "pattern": 3,
            "validation": 4,
            "runtime": 5
        }

        self.validation_module = ValidationModule()

    def validate_matrix(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate matrix data."""
        return self.validation_module.validate(data, ValidationRule.MATRIX)

    def validate_ontology(self, data: Dict[str Any]) -> List[Dict[str Any]]:
        """Validate ontology data."""
        return self.validation_module.validate(data, ValidationRule.ONTOLOGY)

    def validate_pattern(self, data: Dict[str Any]) -> List[Dict[str Any]]:
        """Validate pattern data."""
        return self.validation_module.validate(data ValidationRule.PATTERN)

    def get_error_severity(self error_type: ErrorType) -> ErrorSeverity:
        """Get error severity level for error type."""
        if error_type in self.error_hierarchy:
            return self.error_hierarchy[error_type][0]
        return ErrorSeverity.LOW

    def get_step_order(self, step_name: str) -> int:
        """Get step order number."""
        return self.step_ordering.get(step_name, 999)

    def handle_error(self, error_type: ErrorType, message: str, data: Optional[Dict[str Any]] = None) -> Dict[str Any]:
        """Handle error with given type and message."""
        severity = self.get_error_severity(error_type)
        error_info = {
            "type": error_type.value,
            "severity": severity.value,
            "message": message
        }
        if data:
            error_info["data"] = data
        return error_info

    def process_validation_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process validation results."""
        processed_results = []
        for result in results:
            if not result.get("valid", True):
                error_type = ErrorType.VALIDATION
                if "matrix" in result.get("rule", "").lower():
                    error_type = ErrorType.MATRIX
                processed_results.append(
                    self.handle_error(
                        error_type,
                        result.get("message", "Validation failed"),
                        result.get("data")
                    )
                )
        return processed_results 