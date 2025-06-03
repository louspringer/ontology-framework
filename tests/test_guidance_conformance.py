import unittest
import logging
import traceback
import shutil
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
from ontology_framework.spore_validation import SporeValidator
from ontology_framework.spore_integration import SporeIntegrator, GUIDANCE
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
TEST = Namespace("http://example.org/test#")
SPORE = Namespace("http://example.org/spores/")
STEP = Namespace("http://example.org/steps/")
PROCESS = Namespace("http://example.org/processes/")

class TestGuidanceConformance(unittest.TestCase):
    """Test cases for guidance conformance and conformance levels."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        logger.info("Setting up test environment")
        try:
            # Create test directories
            self.test_data_dir = Path("test_data")
            self.test_data_dir.mkdir(exist_ok=True)
            
            # Create test graph and initialize validator
            self.test_graph = Graph()
            self.validator = SporeValidator(ontology_graph=self.test_graph)
            self.integrator = SporeIntegrator(str(self.test_data_dir))
            
            # Set up guidance ontology
            self.guidance_graph = Graph()
            self.guidance_graph.add((GUIDANCE.STRICT, RDF.type, GUIDANCE.ModelConformance))
            self.guidance_graph.add((GUIDANCE.MODERATE, RDF.type, GUIDANCE.ModelConformance))
            self.guidance_graph.add((GUIDANCE.RELAXED, RDF.type, GUIDANCE.ModelConformance))
            
            # Add required properties to conformance levels
            for level in [GUIDANCE.STRICT, GUIDANCE.MODERATE, GUIDANCE.RELAXED]:
                self.guidance_graph.add((level, GUIDANCE.conformanceLevel, Literal(str(level).split("#")[-1])))
                self.guidance_graph.add((level, GUIDANCE.hasValidationRules, Literal(True)))
                self.guidance_graph.add((level, GUIDANCE.hasMinimumRequirements, Literal(True)))
                self.guidance_graph.add((level, GUIDANCE.hasComplianceMetrics, Literal(True)))
            
            # Register namespaces in both validator and guidance graphs
            for prefix, ns in [
                ('guidance', GUIDANCE),
                ('test', TEST),
                ('spore', SPORE),
                ('step', STEP),
                ('process', PROCESS),
                ('rdf', RDF),
                ('rdfs', RDFS),
                ('owl', OWL),
                ('sh', SH)
            ]:
                self.validator.graph.bind(prefix, ns)
                self.guidance_graph.bind(prefix, ns)
            
            # Set the guidance graph in the integrator
            self.integrator.guidance_graph = self.guidance_graph
            self.test_spore = SPORE['test-spore']
            self.target_model = TEST['target-model']
            
            # Create test model with conformance rules
            self._create_test_model()
            logger.info("Test environment setup complete")
        except Exception as e:
            logger.error(f"Failed to set up test environment: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _create_test_model(self) -> None:
        """Create a test model file with conformance rules."""
        logger.debug("Creating test model file with conformance rules")
        try:
            model_path = self.test_data_dir / "test_model.ttl"
            with open(model_path, 'w') as f:
                f.write("""@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix test: <http://example.org/test#> .
@prefix guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .

test:TargetModel a owl:Ontology ;
    rdfs:label "Target Model" ;
    rdfs:comment "A target model for spore integration" ;
    owl:versionInfo "1.0.0" ;
    guidance:hasConformanceCheck test:ModelConformance .

test:ModelConformance a guidance:ModelConformance ;
    guidance:conformanceLevel "STRICT" ;
    guidance:requiresPrefixValidation true ;
    guidance:requiresNamespaceValidation true .

test:TargetClass a owl:Class ;
    rdfs:label "Target Class" ;
    rdfs:comment "A target class for spore integration" ;
    owl:versionInfo "1.0.0" .
""")
            logger.info("Test model file created successfully")
        except Exception as e:
            logger.error(f"Failed to create test model file: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_conformance_level_validation(self) -> None:
        """Test conformance level validation."""
        logger.info("Testing conformance level validation")
        try:
            # Test STRICT conformance
            self.integrator.set_conformance_level(GUIDANCE.STRICT)
            result = self.integrator.validate_conformance(self.target_model)
            self.assertTrue(result)
            
            # Test MODERATE conformance
            self.integrator.set_conformance_level(GUIDANCE.MODERATE)
            result = self.integrator.validate_conformance(self.target_model)
            self.assertTrue(result)
            
            # Test RELAXED conformance
            self.integrator.set_conformance_level(GUIDANCE.RELAXED)
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

    def test_prefix_validation(self) -> None:
        """Test prefix validation."""
        logger.info("Testing prefix validation")
        try:
            # Create spore with valid prefix
            self.validator.graph.add((self.test_spore, RDF.type, GUIDANCE.TransformationPattern))
            self.validator.graph.add((self.test_spore, GUIDANCE.targetModel, self.target_model))
            
            # Test with prefix validation required
            self.integrator.set_conformance_level("STRICT")
            result = self.integrator.validate_prefixes(self.test_spore)
            self.assertTrue(result)
            
            # Test with invalid prefix
            invalid_spore = URIRef("http://invalid.org/spores/invalid")
            self.validator.graph.add((invalid_spore, RDF.type, GUIDANCE.TransformationPattern))
            with self.assertRaises(ConformanceError):
                self.integrator.validate_prefixes(invalid_spore)
            
            logger.info("Prefix validation test passed")
        except Exception as e:
            logger.error(f"Prefix validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_namespace_validation(self) -> None:
        """Test namespace validation."""
        logger.info("Testing namespace validation")
        try:
            # Create spore with valid namespace
            self.validator.graph.add((self.test_spore, RDF.type, GUIDANCE.TransformationPattern))
            self.validator.graph.add((self.test_spore, GUIDANCE.targetModel, self.target_model))
            
            # Test with namespace validation required
            self.integrator.set_conformance_level("STRICT")
            result = self.integrator.validate_namespaces(self.test_spore)
            self.assertTrue(result)
            
            # Test with invalid namespace
            invalid_spore = URIRef("http://invalid.org/spores/invalid")
            self.validator.graph.add((invalid_spore, RDF.type, GUIDANCE.TransformationPattern))
            with self.assertRaises(ConformanceError):
                self.integrator.validate_namespaces(invalid_spore)
            
            logger.info("Namespace validation test passed")
        except Exception as e:
            logger.error(f"Namespace validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_integration_step_validation(self) -> None:
        """Test integration step validation."""
        logger.info("Testing integration step validation")
        try:
            # Create integration process
            process = PROCESS['test-process']
            self.validator.graph.add((process, RDF.type, GUIDANCE.IntegrationProcess))
            
            # Add integration steps
            step1 = STEP['step1']
            step2 = STEP['step2']
            
            # Add steps to process with proper ordering
            self.validator.graph.add((process, GUIDANCE.hasIntegrationStep, step1))
            self.validator.graph.add((process, GUIDANCE.hasIntegrationStep, step2))
            
            # Add step metadata
            for step, order in [(step1, 1), (step2, 2)]:
                self.validator.graph.add((step, RDF.type, GUIDANCE.IntegrationStep))
                self.validator.graph.add((step, GUIDANCE.stepOrder, Literal(order)))
                self.validator.graph.add((step, GUIDANCE.stepDescription, Literal(f"Step {order}")))
                self.validator.graph.add((step, GUIDANCE.stepTarget, self.target_model))
                self.validator.graph.add((step, GUIDANCE.stepType, GUIDANCE.TransformationStep))
            
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

    def test_ordered_step_execution(self) -> None:
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

    def test_step_type_validation(self) -> None:
        """Test step type validation."""
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

    def test_step_target_validation(self) -> None:
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

    def test_step_metadata_validation(self) -> None:
        """Test step metadata validation."""
        logger.info("Testing step metadata validation")
        try:
            # Create integration process
            process = URIRef("http://example.org/processes/test-process")
            self.validator.graph.add((process, RDF.type, GUIDANCE.IntegrationProcess))
            
            # Add step with missing metadata
            step = URIRef("http://example.org/steps/missing-metadata-step")
            self.validator.graph.add((step, RDF.type, GUIDANCE.TransformationStep))
            self.validator.graph.add((step, GUIDANCE.stepOrder, Literal(1)))
            self.validator.graph.add((step, GUIDANCE.stepDescription, Literal("Missing metadata")))
            self.validator.graph.add((process, GUIDANCE.hasIntegrationStep, step))
            
            # Add step data to integrator graph
            for triple in self.validator.graph.triples((None, None, None)):
                self.integrator.graph.add(triple)
            
            # Test step execution
            self.integrator.set_conformance_level("STRICT")
            with self.assertRaises(ConformanceError):
                self.integrator.execute_integration_steps(process)
            
            logger.info("Step metadata validation test passed")
        except Exception as e:
            logger.error(f"Step metadata validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_step_dependency_validation(self) -> None:
        """Test validation of step dependencies."""
        logger.info("Testing step dependency validation")
        try:
            # Create integration process
            process = URIRef("http://example.org/processes/test-process")
            self.validator.graph.add((process, RDF.type, GUIDANCE.IntegrationProcess))
            
            # Add step with missing dependency
            step = URIRef("http://example.org/steps/missing-dependency-step")
            self.validator.graph.add((step, RDF.type, GUIDANCE.TransformationStep))
            self.validator.graph.add((step, GUIDANCE.stepOrder, Literal(1)))
            self.validator.graph.add((step, GUIDANCE.stepDescription, Literal("Missing dependency")))
            self.validator.graph.add((process, GUIDANCE.hasIntegrationStep, step))
            
            # Add step data to integrator graph
            for triple in self.validator.graph.triples((None, None, None)):
                self.integrator.graph.add(triple)
            
            # Test step execution
            self.integrator.set_conformance_level("STRICT")
            with self.assertRaises(ConformanceError):
                self.integrator.execute_integration_steps(process)
            
            logger.info("Step dependency validation test passed")
        except Exception as e:
            logger.error(f"Step dependency validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_step_execution_validation(self) -> None:
        """Test validation of step execution."""
        logger.info("Testing step execution validation")
        try:
            # Create integration process
            process = URIRef("http://example.org/processes/test-process")
            self.validator.graph.add((process, RDF.type, GUIDANCE.IntegrationProcess))
            
            # Add step with invalid execution
            step = URIRef("http://example.org/steps/invalid-execution-step")
            self.validator.graph.add((step, RDF.type, GUIDANCE.TransformationStep))
            self.validator.graph.add((step, GUIDANCE.stepOrder, Literal(1)))
            self.validator.graph.add((step, GUIDANCE.stepDescription, Literal("Invalid execution")))
            self.validator.graph.add((process, GUIDANCE.hasIntegrationStep, step))
            
            # Add step data to integrator graph
            for triple in self.validator.graph.triples((None, None, None)):
                self.integrator.graph.add(triple)
            
            # Test step execution
            self.integrator.set_conformance_level("STRICT")
            with self.assertRaises(ConformanceError):
                self.integrator.execute_integration_steps(process)
            
            logger.info("Step execution validation test passed")
        except Exception as e:
            logger.error(f"Step execution validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def test_type_validation(self) -> None:
        """Test validation of type constraints."""
        logger.info("Testing type validation")
        try:
            # Create integration process
            process = URIRef("http://example.org/processes/test-process")
            self.validator.graph.add((process, RDF.type, GUIDANCE.IntegrationProcess))
            
            # Add step with invalid type
            step = URIRef("http://example.org/steps/invalid-type-step")
            self.validator.graph.add((step, RDF.type, RDF.Property))  # Invalid type
            self.validator.graph.add((step, GUIDANCE.stepOrder, Literal(1)))
            self.validator.graph.add((step, GUIDANCE.stepDescription, Literal("Invalid type")))
            self.validator.graph.add((process, GUIDANCE.hasIntegrationStep, step))
            
            # Add step data to integrator graph
            for triple in self.validator.graph.triples((None, None, None)):
                self.integrator.graph.add(triple)
            
            # Test step execution
            self.integrator.set_conformance_level("STRICT")
            with self.assertRaises(ConformanceError):
                self.integrator.execute_integration_steps(process)
            
            logger.info("Type validation test passed")
        except Exception as e:
            logger.error(f"Type validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def tearDown(self) -> None:
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