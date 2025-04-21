"""Tests for spore integration functionality."""

import unittest
import logging
import tempfile
from pathlib import Path
from typing import Optional
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL

from ontology_framework.spore_integration import SporeIntegrator
from ontology_framework.spore_validation import SporeValidator
from ontology_framework.exceptions import ConcurrentModificationError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define test namespaces
TEST = Namespace("http://example.org/test#")
META = Namespace("http://example.org/guidance#")

class TestSporeIntegration(unittest.TestCase):
    """Test cases for SporeIntegrator class."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp()
        logger.info(f"Created test directory: {self.test_dir}")
        
        # Initialize validator and integrator
        self.validator_graph = Graph()
        self.validator = SporeValidator(ontology_graph=self.validator_graph)
        self.integrator = SporeIntegrator(self.test_dir)
        
        # Set up test data
        self.test_model = URIRef(TEST.TestModel)
        self.test_spore = URIRef(TEST.TestSpore)
        self.test_patch = URIRef(TEST.TestPatch)
        
        # Add test data to graphs
        self.integrator.graph.add((self.test_spore, RDF.type, META.Spore))
        self.integrator.graph.add((self.test_spore, META.targetModel, self.test_model))
        self.integrator.graph.add((self.test_spore, META.distributesPatch, self.test_patch))
        self.integrator.graph.add((self.test_patch, RDF.type, META.ConceptPatch))
        
        # Add required properties to test spore
        self.integrator.graph.add((self.test_spore, OWL.versionInfo, Literal("1.0.0")))
        self.integrator.graph.add((self.test_spore, RDFS.label, Literal("Test Spore")))
        self.integrator.graph.add((self.test_spore, RDFS.comment, Literal("A test spore for integration testing")))
        
        # Add validation data
        self.validator_graph.add((self.test_spore, RDF.type, META.Spore))
        self.validator_graph.add((self.test_spore, META.targetModel, self.test_model))
        self.validator_graph.add((self.test_spore, OWL.versionInfo, Literal("1.0.0")))
        self.validator_graph.add((self.test_spore, RDFS.label, Literal("Test Spore")))
        self.validator_graph.add((self.test_spore, RDFS.comment, Literal("A test spore for integration testing")))
        
        logger.info("Test environment setup completed")

    def test_spore_validation_before_integration(self) -> None:
        """Test that spores are validated before integration."""
        logger.info("Testing spore validation before integration")
        try:
            result = self.integrator.integrate_spore(self.test_spore, self.test_model)
            self.assertTrue(result)
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

    def test_model_compatibility_check(self) -> None:
        """Test compatibility checking between spores and target models."""
        logger.info("Testing model compatibility check")
        try:
            result = self.integrator.check_compatibility(self.test_spore, self.test_model)
            self.assertTrue(result)
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

    def test_patch_application(self) -> None:
        """Test patch application during integration."""
        logger.info("Testing patch application")
        try:
            result = self.integrator.apply_patch(self.test_spore, self.test_patch, self.test_model)
            self.assertTrue(result)
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

    def test_concurrent_integration(self) -> None:
        """Test concurrent integration of multiple spores."""
        logger.info("Testing concurrent integration")
        try:
            # Create additional test spore
            test_spore2 = URIRef(TEST.TestSpore2)
            test_patch2 = URIRef(TEST.TestPatch2)
            
            # Add to graphs
            self.integrator.graph.add((test_spore2, RDF.type, META.Spore))
            self.integrator.graph.add((test_spore2, META.targetModel, self.test_model))
            self.integrator.graph.add((test_spore2, META.distributesPatch, test_patch2))
            self.integrator.graph.add((test_patch2, RDF.type, META.ConceptPatch))
            
            # Add required properties to test_spore2
            self.integrator.graph.add((test_spore2, OWL.versionInfo, Literal("1.0.0")))
            self.integrator.graph.add((test_spore2, RDFS.label, Literal("Test Spore 2")))
            self.integrator.graph.add((test_spore2, RDFS.comment, Literal("A second test spore for concurrent integration testing")))
            
            self.validator_graph.add((test_spore2, RDF.type, META.Spore))
            self.validator_graph.add((test_spore2, META.targetModel, self.test_model))
            self.validator_graph.add((test_spore2, OWL.versionInfo, Literal("1.0.0")))
            self.validator_graph.add((test_spore2, RDFS.label, Literal("Test Spore 2")))
            self.validator_graph.add((test_spore2, RDFS.comment, Literal("A second test spore for concurrent integration testing")))
            
            result = self.integrator.integrate_concurrent([self.test_spore, test_spore2], self.test_model)
            self.assertTrue(result)
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

    def test_version_migration(self) -> None:
        """Test migration of spores to new versions."""
        logger.info("Testing version migration")
        try:
            result = self.integrator.migrate_version(self.test_spore, "2.0.0")
            self.assertTrue(result)
            
            # Verify version was updated
            version = next(self.integrator.graph.objects(self.test_spore, OWL.versionInfo))
            self.assertEqual(str(version), "2.0.0")
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

    def test_dependency_resolution(self) -> None:
        """Test resolution of spore dependencies."""
        logger.info("Testing dependency resolution")
        try:
            # Add test dependency
            test_dependency = URIRef(TEST.TestDependency)
            self.integrator.graph.add((self.test_spore, OWL.imports, test_dependency))
            self.integrator.graph.add((test_dependency, RDF.type, META.TransformationPattern))
            
            result = self.integrator.resolve_dependencies(self.test_spore)
            self.assertTrue(result)
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

    def test_error_handling(self) -> None:
        """Test error handling for invalid inputs."""
        logger.info("Testing error handling")
        try:
            # Test with invalid spore
            invalid_spore = URIRef(TEST.InvalidSpore)
            with self.assertRaises(ValueError):
                self.integrator.integrate_spore(invalid_spore, self.test_model)
            
            # Test concurrent modification error
            test_spore2 = URIRef(TEST.TestSpore2)
            self.integrator.graph.add((test_spore2, RDF.type, META.Spore))
            self.integrator.graph.add((test_spore2, META.distributesPatch, self.test_patch))
            
            with self.assertRaises(ConcurrentModificationError):
                self.integrator.integrate_concurrent([self.test_spore, test_spore2], self.test_model)
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

    def tearDown(self) -> None:
        """Clean up test environment."""
        logger.info("Cleaning up test environment")
        try:
            # Remove temporary directory
            Path(self.test_dir).rmdir()
            logger.info("Test environment cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main() 