import unittest
import logging
import traceback
import time
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
from ontology_framework.spore_validation import SporeValidator
from ontology_framework.patch_management import PatchManager

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('patch_management_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define namespaces
META = Namespace("http://example.org/guidance#")
TEST = Namespace("http://example.org/test#")

class TestPatchManagement(unittest.TestCase):
    """Test cases for patch management operations."""
    
    def setUp(self):
        """Set up test environment."""
        logger.info("Setting up test environment")
        try:
            # Create test directories
            self.test_data_dir = Path("test_data")
            self.test_data_dir.mkdir(exist_ok=True)
            
            self.validator = SporeValidator()
            self.patch_manager = PatchManager(str(self.test_data_dir))
            self.test_spore = URIRef("http://example.org/spores/test-spore")
            self.test_patch = URIRef("http://example.org/patches/test-patch")
            
            # Create test patch
            self._create_test_patch()
            logger.info("Test environment setup complete")
        except Exception as e:
            logger.error(f"Failed to set up test environment: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _create_test_patch(self):
        """Create a test patch file."""
        logger.debug("Creating test patch file")
        try:
            patch_path = self.test_data_dir / "test_patch.ttl"
            with open(patch_path, 'w') as f:
                f.write("""@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix test: <http://example.org/test#> .
@prefix meta: <http://example.org/guidance#> .

test:TestPatch
    a meta:ConceptPatch ;
    rdfs:label "Test Patch" ;
    rdfs:comment "A test patch for validation" ;
    owl:versionInfo "1.0.0" ;
    meta:patchOperation [
        a meta:AddOperation ;
        meta:targetClass test:TargetClass ;
        meta:addProperty [
            a owl:ObjectProperty ;
            rdfs:label "New Property" ;
            rdfs:comment "A new property added by the patch"
        ]
    ] .
""")
            logger.info("Test patch file created successfully")
        except Exception as e:
            logger.error(f"Failed to create test patch file: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_patch_creation(self):
        """Test patch creation and validation."""
        logger.info("Testing patch creation")
        try:
            # Create patch
            patch = self.patch_manager.create_patch(
                self.test_spore,
                "Test Patch",
                "A test patch",
                "1.0.0"
            )
            
            # Validate patch
            result = self.patch_manager.validate_patch(patch)
            self.assertTrue(result)
            logger.info("Patch creation test passed")
        except Exception as e:
            logger.error(f"Patch creation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_patch_application(self):
        """Test patch application to target model."""
        logger.info("Testing patch application")
        try:
            # Create target model
            target_model = URIRef("http://example.org/models/target-model")
            self.validator.graph.add((target_model, RDF.type, OWL.Ontology))
            
            # Apply patch
            result = self.patch_manager.apply_patch(self.test_patch, target_model)
            self.assertTrue(result)
            logger.info("Patch application test passed")
        except Exception as e:
            logger.error(f"Patch application test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_patch_rollback(self):
        """Test patch rollback functionality."""
        logger.info("Testing patch rollback")
        try:
            # Create target model
            target_model = URIRef("http://example.org/models/target-model")
            self.validator.graph.add((target_model, RDF.type, OWL.Ontology))
            
            # Apply and rollback patch
            self.patch_manager.apply_patch(self.test_patch, target_model)
            result = self.patch_manager.rollback_patch(self.test_patch, target_model)
            self.assertTrue(result)
            logger.info("Patch rollback test passed")
        except Exception as e:
            logger.error(f"Patch rollback test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_patch_dependencies(self):
        """Test patch dependency management."""
        logger.info("Testing patch dependencies")
        try:
            # Create dependent patch
            dependent_patch = URIRef("http://example.org/patches/dependent-patch")
            self.validator.graph.add((dependent_patch, RDF.type, META.ConceptPatch))
            self.validator.graph.add((dependent_patch, META.dependsOn, self.test_patch))
            
            # Check dependencies
            result = self.patch_manager.check_dependencies(dependent_patch)
            self.assertTrue(result)
            logger.info("Patch dependencies test passed")
        except Exception as e:
            logger.error(f"Patch dependencies test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_patch_versioning(self):
        """Test patch version management."""
        logger.info("Testing patch versioning")
        try:
            # Create versioned patch
            versioned_patch = self.patch_manager.create_patch(
                self.test_spore,
                "Versioned Patch",
                "A versioned patch",
                "1.0.0"
            )
            
            # Update version
            result = self.patch_manager.update_version(versioned_patch, "2.0.0")
            self.assertTrue(result)
            logger.info("Patch versioning test passed")
        except Exception as e:
            logger.error(f"Patch versioning test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_patch_validation(self):
        """Test comprehensive patch validation."""
        logger.info("Testing patch validation")
        try:
            # Test invalid patch type
            invalid_patch = URIRef("http://example.org/patches/invalid-patch")
            self.validator.graph.add((invalid_patch, RDF.type, OWL.Class))
            
            with self.assertRaises(ValueError):
                self.patch_manager.validate_patch(invalid_patch)
            
            # Test missing required properties
            incomplete_patch = URIRef("http://example.org/patches/incomplete-patch")
            self.validator.graph.add((incomplete_patch, RDF.type, META.ConceptPatch))
            
            with self.assertRaises(ValueError):
                self.patch_manager.validate_patch(incomplete_patch)
            
            logger.info("Patch validation test passed")
        except Exception as e:
            logger.error(f"Patch validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_patch_performance(self):
        """Test patch performance impact."""
        logger.info("Testing patch performance")
        try:
            # Create large patch
            large_patch = self.patch_manager.create_patch(
                self.test_spore,
                "Large Patch",
                "A large patch for performance testing",
                "1.0.0"
            )
            
            # Add many operations
            for i in range(1000):
                operation = URIRef(f"http://example.org/operations/op{i}")
                self.validator.graph.add((large_patch, META.patchOperation, operation))
            
            # Measure performance
            start_time = time.time()
            self.patch_manager.apply_patch(large_patch, self.test_spore)
            end_time = time.time()
            
            # Check performance threshold
            self.assertLess(end_time - start_time, 5.0)  # Should complete within 5 seconds
            logger.info("Patch performance test passed")
        except Exception as e:
            logger.error(f"Patch performance test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_error_handling(self):
        """Test comprehensive error handling."""
        logger.info("Testing error handling")
        try:
            # Test invalid inputs
            with self.assertRaises(ValueError):
                self.patch_manager.create_patch(None, "Test", "Test", "1.0.0")
            
            with self.assertRaises(ValueError):
                self.patch_manager.apply_patch(None, self.test_spore)
            
            with self.assertRaises(ValueError):
                self.patch_manager.rollback_patch(None, self.test_spore)
            
            # Test invalid operations
            with self.assertRaises(ValueError):
                self.patch_manager.update_version(None, "2.0.0")
            
            with self.assertRaises(ValueError):
                self.patch_manager.check_dependencies(None)
            
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