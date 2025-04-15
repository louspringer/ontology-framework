import unittest
import logging
import traceback
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
from ontology_framework.spore_validation import SporeValidator
from ontology_framework.spore_integration import SporeIntegrator
from ontology_framework.exceptions import ConcurrentModificationError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spore_integration_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define namespaces
META = Namespace("http://example.org/guidance#")
TEST = Namespace("http://example.org/test#")

class TestSporeIntegration(unittest.TestCase):
    """Test cases for spore integration workflows."""
    
    def setUp(self):
        """Set up test environment."""
        logger.info("Setting up test environment")
        try:
            # Create test directories
            self.test_data_dir = Path("test_data")
            self.test_data_dir.mkdir(exist_ok=True)
            
            self.validator = SporeValidator()
            self.integrator = SporeIntegrator(str(self.test_data_dir))
            self.test_spore = URIRef("http://example.org/spores/test-spore")
            self.target_model = URIRef("http://example.org/models/target-model")
            
            # Create test model
            self._create_test_model()
            logger.info("Test environment setup complete")
        except Exception as e:
            logger.error(f"Failed to set up test environment: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _create_test_model(self):
        """Create a test model file."""
        logger.debug("Creating test model file")
        try:
            model_path = self.test_data_dir / "test_model.ttl"
            with open(model_path, 'w') as f:
                f.write("""@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix test: <http://example.org/test#> .

test:TargetModel
    a owl:Ontology ;
    rdfs:label "Target Model" ;
    rdfs:comment "A target model for spore integration" ;
    owl:versionInfo "1.0.0" .

test:TargetClass
    a owl:Class ;
    rdfs:label "Target Class" ;
    rdfs:comment "A target class for spore integration" ;
    owl:versionInfo "1.0.0" .
""")
            logger.info("Test model file created successfully")
        except Exception as e:
            logger.error(f"Failed to create test model file: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_spore_validation_before_integration(self):
        """Test that spores are validated before integration."""
        logger.info("Testing spore validation before integration")
        try:
            # Create invalid spore
            self.validator.graph.add((self.test_spore, RDF.type, OWL.Class))
            
            with self.assertRaises(ValueError) as cm:
                self.integrator.integrate_spore(self.test_spore, self.target_model)
            logger.debug(f"Expected ValueError raised: {str(cm.exception)}")
            logger.info("Spore validation test passed")
        except Exception as e:
            logger.error(f"Spore validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_model_compatibility_check(self):
        """Test model compatibility checking."""
        logger.info("Testing model compatibility check")
        try:
            # Create compatible spore
            self.validator.graph.add((self.test_spore, RDF.type, META.TransformationPattern))
            self.validator.graph.add((self.test_spore, META.targetModel, self.target_model))
            
            result = self.integrator.check_compatibility(self.test_spore, self.target_model)
            self.assertTrue(result)
            logger.info("Model compatibility check passed")
        except Exception as e:
            logger.error(f"Model compatibility check failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_patch_application(self):
        """Test patch application during integration."""
        logger.info("Testing patch application")
        try:
            # Create spore with patch
            patch = URIRef("http://example.org/patches/test-patch")
            self.validator.graph.add((self.test_spore, RDF.type, META.TransformationPattern))
            self.validator.graph.add((self.test_spore, META.distributesPatch, patch))
            self.validator.graph.add((patch, RDF.type, META.ConceptPatch))
            
            result = self.integrator.apply_patch(self.test_spore, patch, self.target_model)
            self.assertTrue(result)
            logger.info("Patch application test passed")
        except Exception as e:
            logger.error(f"Patch application test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_concurrent_integration(self):
        """Test concurrent spore integration."""
        logger.info("Testing concurrent integration")
        try:
            # Create multiple spores
            spore1 = URIRef("http://example.org/spores/spore1")
            spore2 = URIRef("http://example.org/spores/spore2")
            
            for spore in [spore1, spore2]:
                self.validator.graph.add((spore, RDF.type, META.TransformationPattern))
            
            # Attempt concurrent integration
            with self.assertRaises(ConcurrentModificationError):
                self.integrator.integrate_concurrent([spore1, spore2], self.target_model)
            logger.info("Concurrent integration test passed")
        except Exception as e:
            logger.error(f"Concurrent integration test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_version_migration(self):
        """Test spore version migration."""
        logger.info("Testing version migration")
        try:
            # Create spore with version
            self.validator.graph.add((self.test_spore, RDF.type, META.TransformationPattern))
            self.validator.graph.add((self.test_spore, OWL.versionInfo, Literal("1.0.0")))
            
            # Migrate to new version
            result = self.integrator.migrate_version(self.test_spore, "2.0.0")
            self.assertTrue(result)
            logger.info("Version migration test passed")
        except Exception as e:
            logger.error(f"Version migration test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_dependency_resolution(self):
        """Test spore dependency resolution."""
        logger.info("Testing dependency resolution")
        try:
            # Create spore with dependency
            dependency = URIRef("http://example.org/spores/dependency")
            self.validator.graph.add((self.test_spore, RDF.type, META.TransformationPattern))
            self.validator.graph.add((self.test_spore, OWL.imports, dependency))
            
            # Resolve dependencies
            result = self.integrator.resolve_dependencies(self.test_spore)
            self.assertTrue(result)
            logger.info("Dependency resolution test passed")
        except Exception as e:
            logger.error(f"Dependency resolution test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling(self):
        """Test comprehensive error handling."""
        logger.info("Testing error handling")
        try:
            # Test invalid spore
            with self.assertRaises(ValueError):
                self.integrator.integrate_spore(None, self.target_model)
            
            # Test invalid model
            with self.assertRaises(ValueError):
                self.integrator.integrate_spore(self.test_spore, None)
            
            # Test invalid patch
            with self.assertRaises(ValueError):
                self.integrator.apply_patch(self.test_spore, None, self.target_model)
            
            logger.info("Error handling test passed")
        except Exception as e:
            logger.error(f"Error handling test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def tearDown(self):
        """Clean up test environment."""
        logger.info("Cleaning up test environment")
        try:
            # Remove test files
            if self.test_data_dir.exists():
                for file in self.test_data_dir.glob("*"):
                    file.unlink()
                self.test_data_dir.rmdir()
            logger.info("Test environment cleanup complete")
        except Exception as e:
            logger.error(f"Failed to clean up test environment: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

if __name__ == '__main__':
    unittest.main() 