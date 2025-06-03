import unittest
import logging
import traceback
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
from rdflib.plugins.sparql import prepareQuery
from datetime import datetime
from ontology_framework.modules.error_handling import (
    ErrorHandler,
    ErrorType,
    ValidationRule,
    ErrorResult
)
from ontology_framework.meta import META

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
            ErrorType.VALIDATION, "Test validation error"
        )
        
        # Verify error info
        self.assertEqual(result["type"], ErrorType.VALIDATION.value)
        self.assertEqual(result["message"], "Test validation error")
        self.assertIn("severity", result)
        
    def test_validate_matrix(self):
        """Test matrix validation"""
        matrix_data = {
            "matrix_id": "test_matrix",
            "matrix_type": "risk",
            "matrix_level": "high"
        }
        result = self.handler.validate_matrix(matrix_data)
        self.assertTrue(isinstance(result, list))
        
    def test_validate_pattern(self):
        """Test pattern validation"""
        pattern_data = {
            "pattern_id": "test_pattern",
            "pattern_type": "structural"
        }
        result = self.handler.validate_pattern(pattern_data)
        self.assertTrue(isinstance(result, list))
    
    def test_error_metrics(self):
        """Test error metrics collection"""
        # Handle multiple errors
        for _ in range(3):
            result = self.handler.handle_error(
                ErrorType.RUNTIME, "Test runtime error"
            )
            self.assertIsInstance(result, dict)
            self.assertEqual(result["type"], ErrorType.RUNTIME.value)
        
        # Handle one more error
        result = self.handler.handle_error(
            ErrorType.API, "Test API error"
        )
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], ErrorType.API.value)
        self.assertIn("severity", result)
        self.assertEqual(result["message"], "Test API error")

if __name__ == '__main__':
    unittest.main()
