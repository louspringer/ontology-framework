import unittest
import logging
import traceback
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
from ontology_framework.spore_validation import SporeValidator
from ontology_framework.spore_integration import SporeIntegrator
from ontology_framework.exceptions import ConcurrentModificationError, ConformanceError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('guidance_conformance_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define namespaces
GUIDANCE = Namespace("http://example.org/guidance#")
META = Namespace("http://example.org/guidance#")
TEST = Namespace("http://example.org/test#")

class TestGuidanceConformance(unittest.TestCase):
    """Test cases for guidance conformance and conformance levels."""
    
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
            
            # Create test model with conformance rules
            self._create_test_model()
            logger.info("Test environment setup complete")
        except Exception as e:
            logger.error(f"Failed to set up test environment: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _create_test_model(self):
        """Create a test model file with conformance rules."""
        logger.debug("Creating test model file with conformance rules")
        try:
            model_path = self.test_data_dir / "test_model.ttl"
            with open(model_path, 'w') as f:
                f.write("""@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix test: <http://example.org/test#> .
@prefix guidance: <http://example.org/guidance#> .

test:TargetModel
    a owl:Ontology ;
    rdfs:label "Target Model" ;
    rdfs:comment "A target model for spore integration" ;
    owl:versionInfo "1.0.0" ;
    guidance:hasConformanceCheck test:ModelConformance .

test:ModelConformance
    a guidance:ModelConformance ;
    guidance:conformanceLevel "STRICT" ;
    guidance:requiresPrefixValidation true ;
    guidance:requiresNamespaceValidation true .

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

    def test_conformance_level_validation(self):
        """Test conformance level validation."""
        logger.info("Testing conformance level validation")
        try:
            # Test STRICT conformance
            self.integrator.set_conformance_level("STRICT")
            result = self.integrator.validate_conformance(self.target_model)
            self.assertTrue(result)
            
            # Test MODERATE conformance
            self.integrator.set_conformance_level("MODERATE")
            result = self.integrator.validate_conformance(self.target_model)
            self.assertTrue(result)
            
            # Test RELAXED conformance
            self.integrator.set_conformance_level("RELAXED")
            result = self.integrator.validate_conformance(self.target_model)
            self.assertTrue(result)
            
            # Test invalid conformance level
            with self.assertRaises(ConformanceError):
                self.integrator.set_conformance_level("INVALID")
            
            logger.info("Conformance level validation test passed")
        except Exception as e:
            logger.error(f"Conformance level validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_prefix_validation(self):
        """Test prefix validation."""
        logger.info("Testing prefix validation")
        try:
            # Create spore with valid prefix
            self.validator.graph.add((self.test_spore, RDF.type, META.TransformationPattern))
            self.validator.graph.add((self.test_spore, META.targetModel, self.target_model))
            
            # Test with prefix validation required
            self.integrator.set_conformance_level("STRICT")
            result = self.integrator.validate_prefixes(self.test_spore)
            self.assertTrue(result)
            
            # Test with invalid prefix
            invalid_spore = URIRef("http://invalid.org/spores/invalid")
            self.validator.graph.add((invalid_spore, RDF.type, META.TransformationPattern))
            with self.assertRaises(ConformanceError):
                self.integrator.validate_prefixes(invalid_spore)
            
            logger.info("Prefix validation test passed")
        except Exception as e:
            logger.error(f"Prefix validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_namespace_validation(self):
        """Test namespace validation."""
        logger.info("Testing namespace validation")
        try:
            # Create spore with valid namespace
            self.validator.graph.add((self.test_spore, RDF.type, META.TransformationPattern))
            self.validator.graph.add((self.test_spore, META.targetModel, self.target_model))
            
            # Test with namespace validation required
            self.integrator.set_conformance_level("STRICT")
            result = self.integrator.validate_namespaces(self.test_spore)
            self.assertTrue(result)
            
            # Test with invalid namespace
            invalid_spore = URIRef("http://invalid.org/spores/invalid")
            self.validator.graph.add((invalid_spore, RDF.type, META.TransformationPattern))
            with self.assertRaises(ConformanceError):
                self.integrator.validate_namespaces(invalid_spore)
            
            logger.info("Namespace validation test passed")
        except Exception as e:
            logger.error(f"Namespace validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_integration_step_validation(self):
        """Test integration step validation."""
        logger.info("Testing integration step validation")
        try:
            # Create integration process
            process = URIRef("http://example.org/processes/test-process")
            self.validator.graph.add((process, RDF.type, GUIDANCE.IntegrationProcess))
            
            # Add integration steps
            step1 = URIRef("http://example.org/steps/step1")
            step2 = URIRef("http://example.org/steps/step2")
            
            for step, order in [(step1, 1), (step2, 2)]:
                self.validator.graph.add((step, RDF.type, GUIDANCE.IntegrationStep))
                self.validator.graph.add((step, GUIDANCE.stepOrder, Literal(order)))
                self.validator.graph.add((step, GUIDANCE.stepDescription, Literal(f"Step {order}")))
                self.validator.graph.add((process, GUIDANCE.hasIntegrationStep, step))
            
            # Test step validation
            self.integrator.set_conformance_level("STRICT")
            result = self.integrator.validate_integration_steps(process)
            self.assertTrue(result)
            
            # Test with invalid step order
            self.validator.graph.remove((step2, GUIDANCE.stepOrder, Literal(2)))
            self.validator.graph.add((step2, GUIDANCE.stepOrder, Literal(3)))
            with self.assertRaises(ConformanceError):
                self.integrator.validate_integration_steps(process)
            
            logger.info("Integration step validation test passed")
        except Exception as e:
            logger.error(f"Integration step validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_ordered_step_execution(self):
        """Test ordered step execution."""
        logger.info("Testing ordered step execution")
        try:
            # Create integration process
            process = URIRef("http://example.org/processes/test-process")
            self.validator.graph.add((process, RDF.type, GUIDANCE.IntegrationProcess))
            
            # Add integration steps in reverse order
            step1 = URIRef("http://example.org/steps/step1")
            step2 = URIRef("http://example.org/steps/step2")
            step3 = URIRef("http://example.org/steps/step3")
            
            # Add validation step
            self.validator.graph.add((step1, RDF.type, GUIDANCE.ValidationStep))
            self.validator.graph.add((step1, GUIDANCE.stepOrder, Literal(1)))
            self.validator.graph.add((step1, GUIDANCE.stepDescription, Literal("Validate model")))
            self.validator.graph.add((step1, GUIDANCE.validates, self.target_model))
            
            # Add transformation step
            self.validator.graph.add((step2, RDF.type, GUIDANCE.TransformationStep))
            self.validator.graph.add((step2, GUIDANCE.stepOrder, Literal(2)))
            self.validator.graph.add((step2, GUIDANCE.stepDescription, Literal("Transform model")))
            self.validator.graph.add((step2, GUIDANCE.transforms, self.target_model))
            
            # Add merge step
            self.validator.graph.add((step3, RDF.type, GUIDANCE.MergeStep))
            self.validator.graph.add((step3, GUIDANCE.stepOrder, Literal(3)))
            self.validator.graph.add((step3, GUIDANCE.stepDescription, Literal("Merge changes")))
            self.validator.graph.add((step3, GUIDANCE.mergesFrom, self.test_spore))
            self.validator.graph.add((step3, GUIDANCE.mergesTo, self.target_model))
            
            # Link steps to process
            for step in [step1, step2, step3]:
                self.validator.graph.add((process, GUIDANCE.hasIntegrationStep, step))
            
            # Add step data to integrator graph
            for triple in self.validator.graph.triples((None, None, None)):
                self.integrator.graph.add(triple)
            
            # Test step execution
            self.integrator.set_conformance_level("STRICT")
            result = self.integrator.execute_integration_steps(process)
            self.assertTrue(result)
            
            # Test with invalid step order
            self.validator.graph.remove((step2, GUIDANCE.stepOrder, Literal(2)))
            self.validator.graph.add((step2, GUIDANCE.stepOrder, Literal(4)))
            with self.assertRaises(ConformanceError):
                self.integrator.execute_integration_steps(process)
            
            logger.info("Ordered step execution test passed")
        except Exception as e:
            logger.error(f"Ordered step execution test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_step_type_validation(self):
        """Test validation of step types."""
        logger.info("Testing step type validation")
        try:
            # Create integration process
            process = URIRef("http://example.org/processes/test-process")
            self.validator.graph.add((process, RDF.type, GUIDANCE.IntegrationProcess))
            
            # Add step with invalid type
            step = URIRef("http://example.org/steps/invalid-step")
            self.validator.graph.add((step, RDF.type, RDF.Property))  # Invalid type
            self.validator.graph.add((step, GUIDANCE.stepOrder, Literal(1)))
            self.validator.graph.add((step, GUIDANCE.stepDescription, Literal("Invalid step")))
            self.validator.graph.add((process, GUIDANCE.hasIntegrationStep, step))
            
            # Add step data to integrator graph
            for triple in self.validator.graph.triples((None, None, None)):
                self.integrator.graph.add(triple)
            
            # Test step execution
            self.integrator.set_conformance_level("STRICT")
            with self.assertRaises(ConformanceError):
                self.integrator.execute_integration_steps(process)
            
            logger.info("Step type validation test passed")
        except Exception as e:
            logger.error(f"Step type validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_step_target_validation(self):
        """Test validation of step targets."""
        logger.info("Testing step target validation")
        try:
            # Create integration process
            process = URIRef("http://example.org/processes/test-process")
            self.validator.graph.add((process, RDF.type, GUIDANCE.IntegrationProcess))
            
            # Add validation step with missing target
            step = URIRef("http://example.org/steps/validation-step")
            self.validator.graph.add((step, RDF.type, GUIDANCE.ValidationStep))
            self.validator.graph.add((step, GUIDANCE.stepOrder, Literal(1)))
            self.validator.graph.add((step, GUIDANCE.stepDescription, Literal("Validate model")))
            self.validator.graph.add((process, GUIDANCE.hasIntegrationStep, step))
            
            # Add step data to integrator graph
            for triple in self.validator.graph.triples((None, None, None)):
                self.integrator.graph.add(triple)
            
            # Test step execution
            self.integrator.set_conformance_level("STRICT")
            with self.assertRaises(ConformanceError):
                self.integrator.execute_integration_steps(process)
            
            logger.info("Step target validation test passed")
        except Exception as e:
            logger.error(f"Step target validation test failed: {str(e)}")
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