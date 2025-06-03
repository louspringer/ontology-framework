"""
Tests for the error handler module.
"""

import unittest
from datetime import datetime
from ontology_framework.error_handler import ErrorHandler
from ontology_framework.error import Error
from ontology_framework.ontology_types import (
    ErrorType, ErrorSeverity, ErrorStep,
    RiskLevel, ComplianceLevel, SecurityLevel, ValidationRule
)

class TestErrorHandler(unittest.TestCase):
    """Test cases for the ErrorHandler class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.error_handler = ErrorHandler()

    def test_add_error(self) -> None:
        """Test adding an error."""
        error = Error(
            error_type=ErrorType.VALIDATION,
            message="Test error message",
            severity=ErrorSeverity.HIGH,
            step=ErrorStep.IDENTIFICATION,
            details={"risk_level": RiskLevel.MEDIUM}
        )
        self.error_handler.add_error(error)
        errors = self.error_handler.get_errors()
        self.assertEqual(len(errors), 1)
        error_dict = errors[0].to_dict()
        self.assertEqual(error_dict["error_type"], ErrorType.VALIDATION.value)
        self.assertEqual(error_dict["message"], "Test error message")
        self.assertEqual(error_dict["severity"], ErrorSeverity.HIGH.value)
        self.assertEqual(error_dict["step"], ErrorStep.IDENTIFICATION.value)
        self.assertEqual(error_dict["details"]["risk_level"], RiskLevel.MEDIUM)
        self.assertIsInstance(error_dict["timestamp"], str)

    def test_get_errors_by_severity(self) -> None:
        """Test getting errors by severity."""
        error1 = Error(
            error_type=ErrorType.VALIDATION,
            message="High severity error",
            severity=ErrorSeverity.HIGH,
            step=ErrorStep.IDENTIFICATION
        )
        error2 = Error(
            error_type=ErrorType.RUNTIME,
            message="Low severity error",
            severity=ErrorSeverity.LOW,
            step=ErrorStep.IDENTIFICATION
        )
        self.error_handler.add_error(error1)
        self.error_handler.add_error(error2)
        high_severity_errors = self.error_handler.get_errors_by_severity(ErrorSeverity.HIGH)
        self.assertEqual(len(high_severity_errors), 1)
        self.assertEqual(high_severity_errors[0].severity, ErrorSeverity.HIGH)

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
        self.assertTrue(self.error_handler.validate(ValidationRule.RISK, valid_data))
        self.assertFalse(self.error_handler.validate(ValidationRule.RISK, invalid_data))

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
            "compliance_level": ComplianceLevel.CRITICAL
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
        error = Error(
            error_type=ErrorType.VALIDATION,
            message="Test error",
            severity=ErrorSeverity.MEDIUM,
            step=ErrorStep.IDENTIFICATION
        )
        self.error_handler.add_error(error)
        self.assertTrue(self.error_handler.has_errors())
        self.error_handler.clear_errors()
        self.assertFalse(self.error_handler.has_errors())

    def test_validate_performance(self):
        """Test performance validation."""
        # Valid performance data
        valid_data = {
            "type": "performance",
            "severity": ErrorSeverity.HIGH,
            "message": "High response time",
            "metrics": {
                "response_time": 1000,
                "throughput": 100,
                "error_rate": 0.1
            }
        }
        self.assertTrue(self.error_handler.validate_performance(valid_data))

        # Invalid performance data (missing required fields)
        invalid_data = {
            "type": "performance",
            "severity": ErrorSeverity.HIGH,
            "message": "High response time"
        }
        self.assertFalse(self.error_handler.validate_performance(invalid_data))

        # Invalid performance data (negative metrics)
        invalid_metrics = {
            "type": "performance",
            "severity": ErrorSeverity.HIGH,
            "message": "High response time",
            "metrics": {
                "response_time": -1000,
                "throughput": 100,
                "error_rate": 0.1
            }
        }
        self.assertFalse(self.error_handler.validate_performance(invalid_metrics))

    def test_validate_reliability(self):
        """Test reliability validation."""
        # Valid reliability data
        valid_data = {
            "type": "reliability",
            "severity": ErrorSeverity.HIGH,
            "message": "Low MTBF",
            "reliability_metrics": {
                "mtbf": 1000,
                "mttr": 10,
                "availability": 99.9
            }
        }
        self.assertTrue(self.error_handler._validate_reliability(valid_data))

        # Invalid reliability data (missing required fields)
        invalid_data = {
            "type": "reliability",
            "severity": ErrorSeverity.HIGH,
            "message": "Low MTBF"
        }
        self.assertFalse(self.error_handler._validate_reliability(invalid_data))

    def test_validate_availability(self):
        """Test availability validation."""
        # Valid availability data
        valid_data = {
            "type": "availability",
            "severity": ErrorSeverity.HIGH,
            "message": "Low uptime",
            "availability_metrics": {
                "uptime": 1000,
                "downtime": 10,
                "availability_percentage": 99.9
            }
        }
        self.assertTrue(self.error_handler._validate_availability(valid_data))

        # Invalid availability data (invalid percentage)
        invalid_data = {
            "type": "availability",
            "severity": ErrorSeverity.HIGH,
            "message": "Low uptime",
            "availability_metrics": {
                "uptime": 1000,
                "downtime": 10,
                "availability_percentage": 150.0  # Invalid percentage
            }
        }
        self.assertFalse(self.error_handler._validate_availability(invalid_data))

    def test_validate_scalability(self):
        """Test scalability validation."""
        # Valid scalability data
        valid_data = {
            "type": "scalability",
            "severity": ErrorSeverity.HIGH,
            "message": "High latency",
            "scalability_metrics": {
                "throughput": 1000,
                "latency": 10,
                "resource_utilization": 80
            }
        }
        self.assertTrue(self.error_handler.validate_scalability(valid_data))

        # Invalid scalability data (missing required fields)
        invalid_data = {
            "type": "scalability",
            "severity": ErrorSeverity.HIGH,
            "message": "High latency"
        }
        self.assertFalse(self.error_handler.validate_scalability(invalid_data))

    def test_validate_maintainability(self):
        """Test maintainability validation."""
        # Valid maintainability data
        valid_data = {
            "type": "maintainability",
            "severity": ErrorSeverity.HIGH,
            "message": "Low test coverage",
            "maintainability_metrics": {
                "complexity": 10,
                "test_coverage": 80,
                "documentation_score": 90
            }
        }
        self.assertTrue(self.error_handler.validate_maintainability(valid_data))

        # Invalid maintainability data (invalid score ranges)
        invalid_data = {
            "type": "maintainability",
            "severity": ErrorSeverity.HIGH,
            "message": "Low test coverage",
            "maintainability_metrics": {
                "complexity": 10,
                "test_coverage": 150,
                "documentation_score": 90
            }
        }
        self.assertFalse(self.error_handler.validate_maintainability(invalid_data))

    def test_validate_security(self):
        """Test security validation."""
        # Valid security data
        valid_data = {
            "type": "security",
            "severity": ErrorSeverity.HIGH,
            "message": "Security breach detected",
            "security_level": "high"
        }
        self.assertTrue(self.error_handler.validate_security(valid_data))

        # Invalid security data (invalid security level)
        invalid_data = {
            "type": "security",
            "severity": ErrorSeverity.HIGH,
            "message": "Security breach detected",
            "security_level": "invalid"
        }
        self.assertFalse(self.error_handler.validate_security(invalid_data))

    def test_compliance_management(self):
        """Test compliance management methods."""
        # Test update_compliance
        self.error_handler.update_compliance("ISO27001", "high")
        self.assertEqual(self.error_handler.compliance["ISO27001"], "high")

        # Test get_compliance_report
        report = self.error_handler.get_compliance_report()
        self.assertIn("ISO27001", report)
        self.assertEqual(report["ISO27001"], "high")

        # Test check_compliance
        self.assertTrue(self.error_handler.check_compliance("ISO27001", "high"))
        self.assertFalse(self.error_handler.check_compliance("ISO27001", "critical"))

    def test_metrics_management(self):
        """Test metrics management methods."""
        # Test check_metrics_thresholds
        metrics = {
            "response_time": 1000,
            "throughput": 100,
            "error_rate": 0.1
        }
        thresholds = {
            "response_time": 2000,
            "throughput": 50,
            "error_rate": 0.2
        }
        self.assertTrue(self.error_handler.check_metrics_thresholds(metrics, thresholds))

        # Test get_metrics_report
        self.error_handler.metrics = metrics
        report = self.error_handler.get_metrics_report()
        self.assertEqual(report, metrics)

    def test_error_summary(self):
        """Test error summary generation."""
        # Add some errors
        self.error_handler.add_error(Error(
            error_type=ErrorType.VALIDATION,
            message="Test error 1",
            severity=ErrorSeverity.HIGH,
            step=ErrorStep.VALIDATION
        ))
        self.error_handler.add_error(Error(
            error_type=ErrorType.RUNTIME,
            message="Test error 2",
            severity=ErrorSeverity.MEDIUM,
            step=ErrorStep.PREVENTION
        ))

        # Test get_error_summary
        summary = self.error_handler.get_error_summary()
        self.assertEqual(summary["total_errors"], 2)
        self.assertEqual(summary["error_types"]["validation"], 1)
        self.assertEqual(summary["error_types"]["runtime"], 1)
        self.assertEqual(summary["severity_levels"]["high"], 1)
        self.assertEqual(summary["severity_levels"]["medium"], 1)

    def test_step_management(self):
        """Test step management methods."""
        # Test set_current_step
        self.error_handler.set_current_step(ErrorStep.VALIDATION)
        self.assertEqual(self.error_handler.get_current_step(), ErrorStep.VALIDATION)

        # Test step transitions
        self.error_handler.set_current_step(ErrorStep.PREVENTION)
        self.assertEqual(self.error_handler.get_current_step(), ErrorStep.PREVENTION)

        # Test invalid step
        with self.assertRaises(ValueError):
            self.error_handler.set_current_step("invalid_step")

if __name__ == '__main__':
    unittest.main() 