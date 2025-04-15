import unittest
import logging
import traceback
import os
import shutil
from pathlib import Path
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD
from ontology_framework.conformance_tracking import ConformanceTracker, ViolationDetails
from ontology_framework.meta import META

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('conformance_tracking_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define namespaces
TEST = Namespace("http://example.org/test#")

class TestConformanceTracker(unittest.TestCase):
    """Test cases for ConformanceTracker."""
    
    def setUp(self):
        """Set up test environment."""
        logger.info("Setting up test environment")
        try:
            # Create test directories
            self.test_dir = Path("tests/data/conformance")
            self.test_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize tracker
            self.tracker = ConformanceTracker()
            
            # Create test spore
            self.test_spore = TEST.Spore1
            self.tracker.graph.add((self.test_spore, RDF.type, META.SemanticSpore))
            self.tracker.graph.add((self.test_spore, RDFS.label, Literal("Test Spore")))
            
            logger.info("Test environment setup complete")
        except Exception as e:
            logger.error(f"Failed to set up test environment: {str(e)}")
            raise

    def test_record_violation(self):
        """Test recording a violation."""
        logger.info("Testing violation recording")
        try:
            # Record violation
            violation = self.tracker.record_violation(
                self.test_spore,
                "Test Violation",
                "This is a test violation",
                "MissingProperty",
                "High"
            )
            
            # Verify violation was recorded
            self.assertIsNotNone(violation)
            self.assertTrue((violation, RDF.type, META.ConformanceViolation) in self.tracker.graph)
            self.assertTrue((violation, RDFS.label, Literal("Test Violation")) in self.tracker.graph)
            self.assertTrue((violation, RDFS.comment, Literal("This is a test violation")) in self.tracker.graph)
            self.assertTrue((violation, META.violationType, META.MissingProperty) in self.tracker.graph)
            self.assertTrue((violation, META.severity, META.High) in self.tracker.graph)
            self.assertTrue((violation, META.affects, self.test_spore) in self.tracker.graph)
            
            logger.info("Violation recording test passed")
        except Exception as e:
            logger.error(f"Violation recording test failed: {str(e)}")
            raise

    def test_resolve_violation(self):
        """Test resolving a violation."""
        logger.info("Testing violation resolution")
        try:
            # Record and resolve violation
            violation = self.tracker.record_violation(
                self.test_spore,
                "Test Violation",
                "This is a test violation",
                "MissingProperty",
                "High"
            )
            result = self.tracker.resolve_violation(violation, "Fixed the missing property")
            
            # Verify resolution
            self.assertTrue(result)
            self.assertTrue((violation, META.resolutionComment, Literal("Fixed the missing property")) in self.tracker.graph)
            self.assertTrue((violation, META.resolvedAt, None) not in self.tracker.graph)
            self.assertTrue((violation, META.status, META.Resolved) in self.tracker.graph)
            
            logger.info("Violation resolution test passed")
        except Exception as e:
            logger.error(f"Violation resolution test failed: {str(e)}")
            raise

    def test_get_violation(self):
        """Test getting violation details."""
        logger.info("Testing violation details retrieval")
        try:
            # Record violation
            violation = self.tracker.record_violation(
                self.test_spore,
                "Test Violation",
                "This is a test violation",
                "MissingProperty",
                "High"
            )
            
            # Get details
            details = self.tracker.get_violation(violation)
            
            # Verify details
            self.assertIsNotNone(details)
            self.assertEqual(details.label, "Test Violation")
            self.assertEqual(details.comment, "This is a test violation")
            self.assertEqual(details.type, META.MissingProperty)
            self.assertEqual(details.severity, META.High)
            self.assertIsNotNone(details.timestamp)
            self.assertIsNone(details.resolution)
            self.assertIsNone(details.resolvedAt)
            self.assertIsNone(details.status)
            
            logger.info("Violation details retrieval test passed")
        except Exception as e:
            logger.error(f"Violation details retrieval test failed: {str(e)}")
            raise

    def test_get_violation_history(self):
        """Test getting violation history."""
        logger.info("Testing violation history retrieval")
        try:
            # Record multiple violations
            for i in range(3):
                self.tracker.record_violation(
                    self.test_spore,
                    f"Test Violation {i}",
                    f"This is test violation {i}",
                    "MissingProperty",
                    "High"
                )
            
            # Get history
            history = self.tracker.get_violation_history(self.test_spore)
            
            # Verify history
            self.assertEqual(len(history), 3)
            self.assertTrue(all(isinstance(row, ViolationDetails) for row in history))
            
            logger.info("Violation history retrieval test passed")
        except Exception as e:
            logger.error(f"Violation history retrieval test failed: {str(e)}")
            raise

    def test_get_violation_statistics(self):
        """Test getting violation statistics."""
        logger.info("Testing violation statistics retrieval")
        try:
            # Record violations of different severities
            self.tracker.record_violation(self.test_spore, "High", "High severity", "MissingProperty", "High")
            self.tracker.record_violation(self.test_spore, "Medium", "Medium severity", "MissingProperty", "Medium")
            self.tracker.record_violation(self.test_spore, "Low", "Low severity", "MissingProperty", "Low")
            
            # Resolve one violation
            violation = self.tracker.record_violation(self.test_spore, "Resolved", "Resolved", "MissingProperty", "High")
            self.tracker.resolve_violation(violation, "Fixed")
            
            # Get statistics
            stats = self.tracker.get_violation_statistics(self.test_spore)
            
            # Verify statistics
            self.assertEqual(stats["total"], 4)
            self.assertEqual(stats["high"], 2)
            self.assertEqual(stats["medium"], 1)
            self.assertEqual(stats["low"], 1)
            self.assertEqual(stats["resolved"], 1)
            
            logger.info("Violation statistics retrieval test passed")
        except Exception as e:
            logger.error(f"Violation statistics retrieval test failed: {str(e)}")
            raise

    def test_notify_violation(self):
        """Test violation notification."""
        logger.info("Testing violation notification")
        try:
            # Record violation
            violation = self.tracker.record_violation(
                self.test_spore,
                "Test Violation",
                "This is a test violation",
                "MissingProperty",
                "High"
            )
            
            # Send notification
            result = self.tracker.notify_violation(violation)
            
            # Verify notification
            self.assertTrue(result)
            
            logger.info("Violation notification test passed")
        except Exception as e:
            logger.error(f"Violation notification test failed: {str(e)}")
            raise

    def test_export_violations(self):
        """Test exporting violations."""
        logger.info("Testing violation export")
        try:
            # Record violation
            self.tracker.record_violation(
                self.test_spore,
                "Test Violation",
                "This is a test violation",
                "MissingProperty",
                "High"
            )
            
            # Export violations
            output_path = self.test_dir / "export.ttl"
            result = self.tracker.export_violations(output_path)
            
            # Verify export
            self.assertTrue(result)
            self.assertTrue(output_path.exists())
            
            # Verify exported content
            exported_graph = Graph()
            exported_graph.parse(output_path, format="turtle")
            self.assertTrue((None, RDF.type, META.ConformanceViolation) in exported_graph)
            
            logger.info("Violation export test passed")
        except Exception as e:
            logger.error(f"Violation export test failed: {str(e)}")
            raise

    def test_error_handling(self):
        """Test error handling."""
        logger.info("Testing error handling")
        try:
            # Test invalid spore
            with self.assertRaises(ValueError):
                self.tracker.record_violation(None, "Test", "Test", "MissingProperty", "High")
            
            # Test invalid violation
            with self.assertRaises(ValueError):
                self.tracker.resolve_violation(None, "Test")
            
            # Test invalid output path
            with self.assertRaises(ValueError):
                self.tracker.export_violations(None)
            
            logger.info("Error handling test passed")
        except Exception as e:
            logger.error(f"Error handling test failed: {str(e)}")
            raise

    def tearDown(self):
        """Clean up test environment."""
        logger.info("Cleaning up test environment")
        try:
            # Remove test directory
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
            
            logger.info("Test environment cleanup complete")
        except Exception as e:
            logger.error(f"Failed to clean up test environment: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main() 