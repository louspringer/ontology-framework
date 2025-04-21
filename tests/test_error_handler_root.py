"""
Tests for the error handler module.
"""

import unittest
from datetime import datetime
from ontology_framework.error_handler import ErrorHandler
from ontology_framework.modules.error_handling.types import (
    ErrorType, ErrorSeverity, ErrorStep, ValidationRule, 
    RiskLevel, ComplianceLevel, SecurityLevel
)

class TestErrorHandler(unittest.TestCase):
    """Test cases for the ErrorHandler class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.error_handler = ErrorHandler()

    def test_add_error(self) -> None:
        """Test adding an error."""
        self.error_handler.add_error(
            ErrorType.VALIDATION,
            "Test error message",
            ErrorSeverity.HIGH,
            ErrorStep.IDENTIFICATION,
            RiskLevel.MEDIUM
        )
        errors = self.error_handler.get_errors()
        self.assertEqual(len(errors), 1)
        error = errors[0]
        self.assertEqual(error["error_type"], ErrorType.VALIDATION)
        self.assertEqual(error["message"], "Test error message")
        self.assertEqual(error["severity"], ErrorSeverity.HIGH)
        self.assertEqual(error["step"], ErrorStep.IDENTIFICATION)
        self.assertEqual(error["risk_level"], RiskLevel.MEDIUM)
        self.assertIsInstance(error["timestamp"], str)

    def test_get_errors_by_severity(self) -> None:
        """Test getting errors by severity."""
        self.error_handler.add_error(
            ErrorType.VALIDATION,
            "High severity error",
            ErrorSeverity.HIGH
        )
        self.error_handler.add_error(
            ErrorType.RUNTIME,
            "Low severity error",
            ErrorSeverity.LOW
        )
        high_severity_errors = self.error_handler.get_errors_by_severity(ErrorSeverity.HIGH)
        self.assertEqual(len(high_severity_errors), 1)
        self.assertEqual(high_severity_errors[0]["severity"], ErrorSeverity.HIGH)

    def test_validate_matrix(self) -> None:
        """Test matrix validation."""
        valid_data = {"matrix": [[1, 2], [3, 4]]}
        invalid_data = {"not_matrix": "invalid"}
        self.assertTrue(self.error_handler.validate(ValidationRule.MATRIX, valid_data))
        self.assertFalse(self.error_handler.validate(ValidationRule.MATRIX, invalid_data))

    def test_validate_risk_assessment(self) -> None:
        """Test risk assessment validation."""
        valid_data = {"risk_level": RiskLevel.HIGH}
        invalid_data = {"risk_level": "invalid"}
        self.assertTrue(self.error_handler.validate(ValidationRule.RISK_ASSESSMENT, valid_data))
        self.assertFalse(self.error_handler.validate(ValidationRule.RISK_ASSESSMENT, invalid_data))

    def test_validate_sensitive_data(self) -> None:
        """Test sensitive data validation."""
        valid_data = {
            "encrypted": True,
            "access_control": SecurityLevel.CONFIDENTIAL
        }
        invalid_data = {"encrypted": True}
        self.assertTrue(self.error_handler.validate(ValidationRule.SENSITIVE_DATA, valid_data))
        self.assertFalse(self.error_handler.validate(ValidationRule.SENSITIVE_DATA, invalid_data))

    def test_validate_compliance(self) -> None:
        """Test compliance validation."""
        valid_data = {
            "standard": "ISO27001",
            "compliance_level": ComplianceLevel.FULL
        }
        invalid_data = {"standard": "ISO27001"}
        self.assertTrue(self.error_handler.validate(ValidationRule.COMPLIANCE, valid_data))
        self.assertFalse(self.error_handler.validate(ValidationRule.COMPLIANCE, invalid_data))

    def test_error_steps(self) -> None:
        """Test error step management."""
        self.assertEqual(self.error_handler.get_current_step(), ErrorStep.IDENTIFICATION)
        self.error_handler.set_current_step(ErrorStep.ANALYSIS)
        self.assertEqual(self.error_handler.get_current_step(), ErrorStep.ANALYSIS)

    def test_error_types(self) -> None:
        """Test error type management."""
        error_types = self.error_handler.get_error_types()
        self.assertIn(ErrorType.VALIDATION, error_types)
        self.assertIn(ErrorType.DATA_LOSS, error_types)
        self.assertEqual(error_types[ErrorType.VALIDATION], "Validation Error")

    def test_validation_rules(self) -> None:
        """Test validation rule management."""
        rules = self.error_handler.get_validation_rules()
        self.assertIn(ValidationRule.MATRIX, rules)
        self.assertIn(ValidationRule.SENSITIVE_DATA, rules)
        self.assertIn(ValidationRule.COMPLIANCE, rules)

    def test_clear_errors(self) -> None:
        """Test clearing errors."""
        self.error_handler.add_error(
            ErrorType.VALIDATION,
            "Test error",
            ErrorSeverity.MEDIUM
        )
        self.assertTrue(self.error_handler.has_errors())
        self.error_handler.clear_errors()
        self.assertFalse(self.error_handler.has_errors())

if __name__ == '__main__':
    unittest.main() 