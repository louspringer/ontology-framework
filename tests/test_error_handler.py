"""Test suite for error handler."""

import unittest
from typing import Dict, List, Optional
from datetime import datetime
from ontology_framework.modules.error_handling import ErrorHandler
from ontology_framework.ontology_types import (
    ErrorType, ErrorSeverity, ErrorStep, ValidationRule,
    SecurityLevel, ComplianceLevel, RiskLevel, PerformanceMetric
)

class TestErrorHandler(unittest.TestCase):
    """Test cases for error handler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()
    
    def test_error_handling_steps(self):
        """Test error handling step ordering."""
        # Verify step order
        self.assertEqual(self.handler.step_ordering["matrix"], 1)
        self.assertEqual(self.handler.step_ordering["ontology"], 2)
        self.assertEqual(self.handler.step_ordering["pattern"], 3)
        self.assertEqual(self.handler.step_ordering["validation"], 4)
        self.assertEqual(self.handler.step_ordering["runtime"], 5)
    
    def test_error_handling_validations(self):
        """Test validation rule handling."""
        # Verify validation rules
        self.assertIn(ValidationRule.MATRIX, self.handler.validation_rules)
        self.assertIn(ValidationRule.ONTOLOGY, self.handler.validation_rules)
        self.assertIn(ValidationRule.PATTERN, self.handler.validation_rules)
    
    def test_error_severity_hierarchy(self):
        """Test error severity hierarchy."""
        # Verify error severity hierarchy
        self.assertEqual(
            self.handler.get_error_severity(ErrorType.MATRIX), ErrorSeverity.CRITICAL
        )
        self.assertEqual(
            self.handler.get_error_severity(ErrorType.VALIDATION), ErrorSeverity.HIGH
        )
        self.assertEqual(
            self.handler.get_error_severity(ErrorType.RUNTIME), ErrorSeverity.MEDIUM
        )
    
    def test_error_handling_process(self):
        """Test the complete error handling process."""
        # Test matrix validation
        matrix_data = {
            "matrix_id": "test_matrix",
            "matrix_type": "risk",
            "matrix_level": "high"
        }
        result = self.handler.validate_matrix(matrix_data)
        self.assertTrue(isinstance(result, list))
        
        # Test ontology validation
        ontology_data = {
            "ontology_id": "test_ontology",
            "ontology_type": "owl"
        }
        result = self.handler.validate_ontology(ontology_data)
        self.assertTrue(isinstance(result, list))
        
        # Test pattern validation
        pattern_data = {
            "pattern_id": "test_pattern",
            "pattern_type": "structural"
        }
        result = self.handler.validate_pattern(pattern_data)
        self.assertTrue(isinstance(result, list))
        
        # Test error handling
        error_info = self.handler.handle_error(
            error_type=ErrorType.VALIDATION,
            message="Test validation error",
            data={"test": "data"}
        )
        self.assertEqual(error_info["type"], ErrorType.VALIDATION.value)
        self.assertEqual(error_info["message"], "Test validation error")
        self.assertIn("severity", error_info)
        self.assertIn("data", error_info)
        
        # Test validation result processing
        validation_results = [
            {
                "valid": False,
                "rule": "matrix_validation",
                "message": "Matrix validation failed",
                "data": {"field": "matrix_type"}
            }
        ]
        processed_results = self.handler.process_validation_results(validation_results)
        self.assertEqual(len(processed_results), 1)
        self.assertEqual(processed_results[0]["type"], ErrorType.MATRIX.value)

if __name__ == '__main__':
    unittest.main() 