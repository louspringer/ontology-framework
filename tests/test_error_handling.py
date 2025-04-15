import unittest
import logging
import traceback
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
from rdflib.plugins.sparql import prepareQuery
from datetime import datetime
from src.ontology_framework.error_handling import (
    ErrorHandler,
    ErrorType,
    ValidationRule,
    ErrorResult
)
from src.ontology_framework.meta import META

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error_handling_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define namespaces
TEST = Namespace("http://example.org/test#")

class TestErrorHandler(unittest.TestCase):
    """Test cases for the ErrorHandler class"""
    
    def setUp(self):
        """Set up test environment"""
        self.handler = ErrorHandler()
    
    def test_handle_error(self):
        """Test error handling process"""
        result = self.handler.handle_error(
            ErrorType.VALIDATION_ERROR,
            "Test validation error"
        )
        
        # Verify process completion
        self.assertTrue(result.identification_complete)
        self.assertTrue(result.analysis_complete)
        self.assertTrue(result.recovery_complete)
        self.assertTrue(result.prevention_complete)
        
        # Verify timestamps
        self.assertIsInstance(result.identification_time, datetime)
        self.assertIsInstance(result.analysis_time, datetime)
        self.assertIsInstance(result.recovery_time, datetime)
        self.assertIsInstance(result.prevention_time, datetime)
        
        # Verify metrics
        self.assertEqual(result.error_count, 1)
        self.assertGreater(result.error_rate, 0)
        self.assertGreater(result.detection_time_ms, 0)
        self.assertGreater(result.recovery_time_ms, 0)
        self.assertGreater(result.resolution_time_ms, 0)
    
    def test_validate_sensitive_data(self):
        """Test sensitive data validation"""
        result = self.handler.validate_rule(
            ValidationRule.SENSITIVE_DATA,
            {"data": "This is sensitive information"}
        )
        self.assertEqual(
            result.log_message,
            "Sensitive data validation passed"
        )
        
        result = self.handler.validate_rule(
            ValidationRule.SENSITIVE_DATA,
            {"data": "Regular data"}
        )
        self.assertEqual(
            result.log_message,
            "No sensitive data detected"
        )
    
    def test_validate_risk_assessment(self):
        """Test risk assessment validation"""
        test_cases = [
            ("high", "Risk assessment validation passed for high risk"),
            ("medium", "Risk assessment validation passed for medium risk"),
            ("low", "Risk assessment validation passed for low risk"),
            ("invalid", "Invalid risk level")
        ]
        
        for risk_level, expected_message in test_cases:
            result = self.handler.validate_rule(
                ValidationRule.RISK_ASSESSMENT,
                {"risk": risk_level}
            )
            self.assertEqual(result.log_message, expected_message)
    
    def test_validate_matrix(self):
        """Test matrix validation"""
        result = self.handler.validate_rule(
            ValidationRule.MATRIX,
            {"matrix": "confusion_matrix"}
        )
        self.assertEqual(result.log_message, "Matrix validation passed")
        
        result = self.handler.validate_rule(
            ValidationRule.MATRIX,
            {"matrix": 123}  # Invalid type
        )
        self.assertEqual(result.log_message, "Invalid matrix data")
    
    def test_error_metrics(self):
        """Test error metrics collection"""
        # Handle multiple errors
        for _ in range(3):
            self.handler.handle_error(
                ErrorType.RUNTIME_ERROR,
                "Test runtime error"
            )
        
        # Get final result
        result = self.handler.handle_error(
            ErrorType.API_ERROR,
            "Test API error"
        )
        
        # Verify metrics
        self.assertEqual(result.error_count, 4)
        self.assertGreater(result.error_rate, 0)
        self.assertGreater(result.detection_time_ms, 0)
        self.assertGreater(result.recovery_time_ms, 0)
        self.assertGreater(result.resolution_time_ms, 0)

if __name__ == '__main__':
    unittest.main() 