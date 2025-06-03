import unittest
import logging
import traceback
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD
from rdflib.plugins.sparql import prepareQuery
from datetime import datetime, timedelta
import re

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('runtime_error_handling_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define namespaces
ns1 = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/#")

class TestRuntimeErrorHandling(unittest.TestCase):
    """Test cases for runtime error handling model."""
    
    def setUp(self):
        """Set up test environment."""
        logger.info("Setting up test environment")
        try:
            # Load runtime error handling ontology
            self.model_path = Path("guidance/modules/runtime_error_handling.ttl")
            self.graph = Graph()
            self.graph.parse(str(self.model_path), format="turtle")
            
            # Bind namespace
            self.graph.bind('ns1', ns1)
            self.graph.bind('sh', SH)
            
            # Define test queries
            self.error_types_query = prepareQuery("""
                SELECT ?type ?label ?comment WHERE {
                    ?type a ns1:ErrorType ;
                          rdfs:label ?label ;
                          rdfs:comment ?comment .
                }
            """, initNs={"ns1": ns1})
            
            self.error_steps_query = prepareQuery("""
                SELECT ?step ?order ?action WHERE {
                    ?step a ns1:ErrorHandlingStep ;
                          ns1:hasStepOrder ?order ;
                          ns1:hasStepAction ?action .
                }
                ORDER BY ?order
            """, initNs={"ns1": ns1})
            
            self.test_error_steps_query = prepareQuery("""
                SELECT ?step ?order ?action WHERE {
                    ?step a ns1:ErrorHandlingStep ;
                          ns1:hasStepOrder ?order ;
                          ns1:hasStepAction ?action .
                    FILTER (STRSTARTS(STR(?step), "http://example.org/guidance#TestError"))
                }
                ORDER BY ?order
            """, initNs={"ns1": ns1})
            
            logger.info("Test environment setup complete")
        except Exception as e:
            logger.error(f"Failed to set up test environment: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_types(self):
        """Test that all required error types are defined."""
        logger.info("Testing error types")
        try:
            results = list(self.graph.query(self.error_types_query))
            
            # Verify we have all required error types
            required_types = {
                "Validation Error": "Errors in data validation",
                "I/O Error": "Errors in input/output operations",
                "Runtime Error": "General runtime errors",
                "API Error": "Errors in API operations",
                "Test Failure": "Errors in test execution"
            }
            
            found_types = {str(row[1]): str(row[2]) for row in results}
            
            for type_name, comment in required_types.items():
                self.assertIn(type_name, found_types, f"Missing error type: {type_name}")
                self.assertEqual(found_types[type_name], comment,
                               f"Comment mismatch for {type_name}")
            
            logger.info("Error types test passed")
        except Exception as e:
            logger.error(f"Error types test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def tearDown(self):
        """Clean up test environment."""
        logger.info("Cleaning up test environment")
        try:
            # Clean up any test artifacts
            if Path('runtime_error_handling_tests.log').exists():
                Path('runtime_error_handling_tests.log').unlink()
            logger.info("Test environment cleanup complete")
        except Exception as e:
            logger.error(f"Failed to clean up test environment: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

if __name__ == '__main__':
    unittest.main() 