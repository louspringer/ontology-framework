import unittest
import logging
import traceback
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import ClassVar
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
GUIDANCE = Namespace("http://example.org/guidance#")

class TestConformanceTracker(unittest.TestCase):
    """Test cases for ConformanceTracker."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        logger.info("Setting up test environment")
        try:
            # Create test directories
            self.test_dir = Path("tests/data/conformance")
            self.test_dir.mkdir(parents=True, exist_ok=True)
            
            # Create guidance graph
            self.guidance_graph = Graph()
            self.guidance_graph.bind('test', TEST)
            self.guidance_graph.bind('guidance', GUIDANCE)
            
            # Add some test guidance rules
            test_rule = TEST.TestRule
            self.guidance_graph.add((test_rule, RDF.type, GUIDANCE.ValidationRule))
            self.guidance_graph.add((test_rule, RDFS.label, Literal("Test Rule")))
            self.guidance_graph.add((test_rule, RDFS.comment, Literal("A test validation rule")))
            
            # Initialize tracker with guidance graph
            self.tracker = ConformanceTracker(guidance_graph=self.guidance_graph)
            
            # Create test spore
            self.test_spore = TEST.Spore1
            self.tracker.graph.add((self.test_spore, RDF.type, META.SemanticSpore))
            self.tracker.graph.add((self.test_spore, RDFS.label, Literal("Test Spore")))
            
            logger.info("Test environment setup complete")
        except Exception as e:
            logger.error(f"Failed to set up test environment: {str(e)}")
            raise
            
    def tearDown(self) -> None:
        """Clean up test environment."""
        try:
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)
            logger.info("Test environment cleaned up")
        except Exception as e:
            logger.error(f"Failed to clean up test environment: {str(e)}")
            raise
            
    def test_add_violation(self) -> None:
        """Test adding a violation."""
        violation = ViolationDetails(
            spore_id=self.test_spore,
            rule_id=TEST.TestRule,
            severity="ERROR",
            message="Test violation",
            timestamp=datetime.now()
        )
        self.tracker.add_violation(violation)
        self.assertEqual(len(self.tracker.violations), 1)
        
    def test_get_violations(self) -> None:
        """Test retrieving violations."""
        violation = ViolationDetails(
            spore_id=self.test_spore,
            rule_id=TEST.TestRule,
            severity="ERROR",
            message="Test violation",
            timestamp=datetime.now()
        )
        self.tracker.add_violation(violation)
        violations = self.tracker.get_violations()
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].message, "Test violation")
        
    def test_clear_violations(self) -> None:
        """Test clearing violations."""
        violation = ViolationDetails(
            spore_id=self.test_spore,
            rule_id=TEST.TestRule,
            severity="ERROR",
            message="Test violation",
            timestamp=datetime.now()
        )
        self.tracker.add_violation(violation)
        self.tracker.clear_violations()
        self.assertEqual(len(self.tracker.violations), 0)
        
    def test_export_violations(self) -> None:
        """Test exporting violations to file."""
        violation = ViolationDetails(
            spore_id=self.test_spore,
            rule_id=TEST.TestRule,
            severity="ERROR",
            message="Test violation",
            timestamp=datetime.now()
        )
        self.tracker.add_violation(violation)
        export_path = self.test_dir / "violations.ttl"
        self.tracker.export_violations(str(export_path))
        self.assertTrue(export_path.exists())
        
    def test_import_violations(self) -> None:
        """Test importing violations from file."""
        violation = ViolationDetails(
            spore_id=self.test_spore,
            rule_id=TEST.TestRule,
            severity="ERROR",
            message="Test violation",
            timestamp=datetime.now()
        )
        self.tracker.add_violation(violation)
        export_path = self.test_dir / "violations.ttl"
        self.tracker.export_violations(str(export_path))
        
        new_tracker = ConformanceTracker(guidance_graph=self.guidance_graph)
        new_tracker.import_violations(str(export_path))
        self.assertEqual(len(new_tracker.violations), 1)
        
if __name__ == '__main__':
    unittest.main() 