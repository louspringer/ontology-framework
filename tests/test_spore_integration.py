"""Tests for spore integration functionality."""

import unittest
import logging
import tempfile
import os
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
        self.test_dir = tempfile.mkdtemp()
        logger.info("Created test directory: %s", self.test_dir)
        
        # Initialize test graphs
        self.validator_graph = Graph()
        self.validator = SporeValidator(ontology_graph=self.validator_graph)
        self.integrator = SporeIntegrator(self.test_dir)
        
        # Create test data directory
        self.data_dir = os.path.join(self.test_dir, "test_data")
        os.makedirs(self.data_dir)
        
        # Initialize test ontologies
        self.test_ontology = Graph()
        
        # Define URIRefs for test entities
        self.test_spore_uri = URIRef("http://test.example.org/TestSpore")
        self.test_model_uri = URIRef("http://test.example.org/TestModel")
        self.test_patch_uri = URIRef("http://test.example.org/TestPatch")
        
        logger.info("Loading guidance ontology")
        # Get workspace root directory
        workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        guidance_path = os.path.join(workspace_root, "guidance", "modules", "validation", "spores.ttl")
        logger.debug("Loading guidance from: %s", guidance_path)
        
        try:
            # Verify file exists
            if not os.path.exists(guidance_path):
                logger.error("Guidance file not found at: %s", guidance_path)
                logger.debug("Current working directory: %s", os.getcwd())
                logger.debug("Workspace root: %s", workspace_root)
                logger.debug("Directory contents: %s", os.listdir(os.path.dirname(guidance_path)))
                raise FileNotFoundError(f"Guidance file not found at: {guidance_path}")
                
            self.test_ontology.parse(guidance_path, format="turtle")
            logger.debug("Loaded guidance ontology with %d triples", len(self.test_ontology))
            
            # Set up test data
            self._setup_test_data()
            
        except Exception as e:
            logger.error("Failed to load guidance ontology: %s", str(e))
            raise
            
        logger.info("Test environment setup completed")

    def _setup_test_data(self) -> None:
        """Set up test data for SPORE validation and integration tests."""
        logger.info("Setting up test data")
        
        logger.debug(f"Creating test SPORE with URI: {self.test_spore_uri}")
        logger.debug(f"Creating test model with URI: {self.test_model_uri}")
        
        # Add test SPORE data to integrator graph
        self.integrator.graph.add((self.test_spore_uri, RDF.type, URIRef("http://example.org/spore#SPORE")))
        self.integrator.graph.add((self.test_spore_uri, RDFS.label, Literal("Test SPORE")))
        self.integrator.graph.add((self.test_spore_uri, URIRef("http://example.org/spore#version"), Literal("1.0.0")))
        self.integrator.graph.add((self.test_spore_uri, URIRef("http://example.org/spore#targetModel"), self.test_model_uri))
        
        # Add test model data
        self.integrator.graph.add((self.test_model_uri, RDF.type, URIRef("http://example.org/spore#Model")))
        self.integrator.graph.add((self.test_model_uri, RDFS.label, Literal("Test Model")))
        self.integrator.graph.add((self.test_model_uri, URIRef("http://example.org/spore#version"), Literal("1.0.0")))
        
        logger.debug(f"Created test SPORE graph with {len(self.integrator.graph)} triples")
        
        # Create test patch
        logger.debug(f"Creating test patch with URI: {self.test_patch_uri}")
        
        # Add test patch data
        self.integrator.graph.add((self.test_patch_uri, RDF.type, URIRef("http://example.org/spore#Patch")))
        self.integrator.graph.add((self.test_patch_uri, RDFS.label, Literal("Test Patch")))
        self.integrator.graph.add((self.test_patch_uri, URIRef("http://example.org/spore#version"), Literal("1.0.0")))
        self.integrator.graph.add((self.test_patch_uri, URIRef("http://example.org/spore#targetSpore"), self.test_spore_uri))
        
        # Also add to validator graph for validation
        self.validator_graph.add((self.test_spore_uri, RDF.type, URIRef("http://example.org/spore#SPORE")))
        self.validator_graph.add((self.test_spore_uri, RDFS.label, Literal("Test SPORE")))
        self.validator_graph.add((self.test_model_uri, RDF.type, URIRef("http://example.org/spore#Model")))
        self.validator_graph.add((self.test_model_uri, RDFS.label, Literal("Test Model")))
        
        logger.info("Test data setup completed")

    def test_spore_validation_before_integration(self) -> None:
        """Test that spores are validated before integration."""
        logger.info("Testing spore validation before integration")
        try:
            result = self.integrator.integrate_spore(self.test_spore_uri, self.test_model_uri)
            self.assertTrue(result)
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

    def test_model_compatibility_check(self) -> None:
        """Test compatibility checking between spores and target models."""
        logger.info("Testing model compatibility check")
        try:
            result = self.integrator.check_compatibility(self.test_spore_uri, self.test_model_uri)
            self.assertTrue(result)
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

    def test_patch_application(self) -> None:
        """Test patch application during integration."""
        logger.info("Testing patch application")
        try:
            result = self.integrator.apply_patch(self.test_spore_uri, self.test_patch_uri, self.test_model_uri)
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
            self.integrator.graph.add((test_spore2, META.targetModel, self.test_model_uri))
            self.integrator.graph.add((test_spore2, META.distributesPatch, test_patch2))
            self.integrator.graph.add((test_patch2, RDF.type, META.ConceptPatch))
            
            # Add required properties to test_spore2
            self.integrator.graph.add((test_spore2, OWL.versionInfo, Literal("1.0.0")))
            self.integrator.graph.add((test_spore2, RDFS.label, Literal("Test Spore 2")))
            self.integrator.graph.add((test_spore2, RDFS.comment, Literal("A second test spore for concurrent integration testing")))
            
            self.validator_graph.add((test_spore2, RDF.type, META.Spore))
            self.validator_graph.add((test_spore2, META.targetModel, self.test_model_uri))
            self.validator_graph.add((test_spore2, OWL.versionInfo, Literal("1.0.0")))
            self.validator_graph.add((test_spore2, RDFS.label, Literal("Test Spore 2")))
            self.validator_graph.add((test_spore2, RDFS.comment, Literal("A second test spore for concurrent integration testing")))
            
            result = self.integrator.integrate_concurrent([self.test_spore_uri, test_spore2], self.test_model_uri)
            self.assertTrue(result)
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

    def test_version_migration(self) -> None:
        """Test migration of spores to new versions."""
        logger.info("Testing version migration")
        try:
            result = self.integrator.migrate_version(self.test_spore_uri, "2.0.0")
            self.assertTrue(result)
            
            # Verify version was updated
            version = next(self.integrator.graph.objects(self.test_spore_uri, OWL.versionInfo))
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
            self.integrator.graph.add((self.test_spore_uri, OWL.imports, test_dependency))
            self.integrator.graph.add((test_dependency, RDF.type, META.TransformationPattern))
            
            result = self.integrator.resolve_dependencies(self.test_spore_uri)
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
                self.integrator.integrate_spore(invalid_spore, self.test_model_uri)
            
            # Test concurrent modification error
            test_spore2 = URIRef(TEST.TestSpore2)
            self.integrator.graph.add((test_spore2, RDF.type, META.Spore))
            self.integrator.graph.add((test_spore2, META.distributesPatch, self.test_patch_uri))
            
            with self.assertRaises(ConcurrentModificationError):
                self.integrator.integrate_concurrent([self.test_spore_uri, test_spore2], self.test_model_uri)
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise

    def tearDown(self) -> None:
        """Clean up test environment."""
        logger.info("Cleaning up test environment")
        try:
            # Remove temporary directory
            import shutil
            shutil.rmtree(self.test_dir)
            logger.info("Test environment cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            # Don't re-raise cleanup errors


if __name__ == '__main__':
    unittest.main()
