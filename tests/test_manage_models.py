#!/usr/bin/env python3
"""
Test suite for the ontology framework model management module.
"""

import os
import tempfile
import unittest
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD
from ontology_framework.manage_models import ModelManager, ModelQualityError, ModelProjectionError
from unittest.mock import MagicMock, patch
import shutil
import logging
import traceback
import sys
import subprocess
import semver

# Configure test logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_manage_models.log')
    ]
)
logger = logging.getLogger(__name__)

# Test namespaces
TEST = Namespace("http://example.org/test#")

class TestModelManager(unittest.TestCase):
    """Test cases for the ModelManager class."""
    
    def setUp(self):
        """Set up test environment."""
        logger.info("Setting up test environment")
        self.temp_dir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory: {self.temp_dir}")
        
        # Create test data directory
        self.test_data_dir = Path(self.temp_dir) / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        logger.debug(f"Created test data directory: {self.test_data_dir}")
        
        # Create test model file
        self.test_model_path = self.test_data_dir / "test_model.ttl"
        self._create_test_model()
        logger.debug(f"Created test model at: {self.test_model_path}")
        
        # Create guidance ontology
        self.guidance_path = self.test_data_dir / "guidance.ttl"
        self._create_guidance_ontology()
        logger.debug(f"Created guidance ontology at: {self.guidance_path}")
        
        # Initialize ModelManager
        self.manager = ModelManager(base_dir=str(self.test_data_dir))
        logger.info("ModelManager initialized successfully")
        
    def tearDown(self):
        """Clean up test environment."""
        logger.info("Cleaning up test environment")
        shutil.rmtree(self.temp_dir)
        logger.debug(f"Removed temporary directory: {self.temp_dir}")
        
    def _create_test_model(self):
        """Create a test model file with proper prefixes and structure."""
        logger.debug("Creating test model file")
        try:
            with open(self.test_model_path, 'w') as f:
                f.write("""@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix test: <http://example.org/test#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

test:TestOntology
    a owl:Ontology ;
    rdfs:label "Test Model" ;
    rdfs:comment "A test model for validation" ;
    owl:versionInfo "1.0.0" .

test:TestClass
    a owl:Class ;
    rdfs:label "Test Class" ;
    rdfs:comment "A test class" ;
    owl:versionInfo "1.0.0" .

test:hasProperty
    a owl:ObjectProperty ;
    rdfs:label "Has Property" ;
    rdfs:comment "A test object property" ;
    owl:versionInfo "1.0.0" ;
    rdfs:domain test:TestClass ;
    rdfs:range test:TestClass .

# SHACL Shapes
test:ClassShape a sh:NodeShape ;
    sh:targetClass owl:Class ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Class must have exactly one label"
    ] ,
    [
        sh:path rdfs:comment ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Class must have exactly one comment"
    ] ,
    [
        sh:path owl:versionInfo ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:pattern "[0-9]+[.][0-9]+[.][0-9]+" ;
        sh:message "Class must have exactly one version in semantic versioning format"
    ] .

test:OntologyShape a sh:NodeShape ;
    sh:targetClass owl:Ontology ;
    sh:property [
        sh:path owl:versionInfo ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:pattern "[0-9]+[.][0-9]+[.][0-9]+" ;
        sh:message "Ontology must have exactly one version in semantic versioning format"
    ] ,
    [
        sh:path rdfs:comment ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Ontology must have exactly one description"
    ] .
""")
            logger.info("Test model file created successfully")
        except Exception as e:
            logger.error(f"Failed to create test model file: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
    def _create_guidance_ontology(self):
        """Create a minimal guidance ontology."""
        logger.debug("Creating guidance ontology")
        try:
            guidance_graph = Graph()
            guidance_graph.add((TEST.Guidance, RDF.type, OWL.Ontology))
            guidance_graph.add((TEST.Guidance, RDFS.label, Literal("Guidance Ontology")))
            guidance_graph.add((TEST.Guidance, RDFS.comment, Literal("Test guidance ontology")))
            guidance_graph.add((TEST.Guidance, OWL.versionInfo, Literal("1.0.0")))
            guidance_graph.serialize(destination=str(self.guidance_path), format="turtle")
            logger.info("Guidance ontology created successfully")
        except Exception as e:
            logger.error(f"Failed to create guidance ontology: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
    def test_initialization(self):
        """Test ModelManager initialization."""
        logger.info("Testing ModelManager initialization")
        try:
            self.assertIsInstance(self.manager, ModelManager)
            self.assertEqual(str(self.manager.base_dir), str(self.test_data_dir))
            self.assertIsInstance(self.manager.guidance_graph, Graph)
            self.assertEqual(len(self.manager.models), 0)
            logger.info("Initialization test passed")
        except Exception as e:
            logger.error(f"Initialization test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
    def test_load_valid_model(self):
        """Test loading a valid model."""
        logger.info("Testing loading valid model")
        try:
            self.manager.load_model(str(self.test_model_path))
            self.assertIn("test_model", self.manager.models)
            logger.info("Valid model loading test passed")
        except Exception as e:
            logger.error(f"Valid model loading test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
    def test_load_invalid_model(self):
        """Test loading an invalid model."""
        logger.info("Testing loading invalid model")
        try:
            # Create an invalid model
            invalid_path = self.test_data_dir / "invalid_model.ttl"
            with open(invalid_path, 'w') as f:
                f.write("""@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<http://example.org/test#InvalidClass>
    a owl:Class .
""")
            
            with self.assertRaises(ValueError):
                self.manager.load_model(str(invalid_path))
            logger.info("Invalid model loading test passed")
        except Exception as e:
            logger.error(f"Invalid model loading test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
    def test_validate_model(self):
        """Test model validation."""
        # Create a valid model
        model_graph = Graph()
        model_graph.add((TEST.ValidClass, RDF.type, OWL.Class))
        model_graph.add((TEST.ValidClass, RDFS.label, Literal("Valid Class")))
        model_graph.add((TEST.ValidClass, RDFS.comment, Literal("A valid class")))
        model_graph.add((TEST.ValidClass, OWL.versionInfo, Literal("1.0.0")))
        
        # Validate the model
        self.manager._validate_model(model_graph)  # Should not raise an exception
        
        # Create an invalid model
        invalid_graph = Graph()
        invalid_graph.add((TEST.InvalidClass, RDF.type, OWL.Class))
        
        # Validate the invalid model
        with self.assertRaises(ValueError):
            self.manager._validate_model(invalid_graph)
            
    def test_integrate_models(self):
        """Test model integration."""
        # Create source models
        model1_path = self.test_data_dir / "model1.ttl"
        model1_graph = Graph()
        model1_graph.add((TEST.Class1, RDF.type, OWL.Class))
        model1_graph.add((TEST.Class1, RDFS.label, Literal("Class 1")))
        model1_graph.add((TEST.Class1, RDFS.comment, Literal("First class")))
        model1_graph.add((TEST.Class1, OWL.versionInfo, Literal("1.0.0")))
        model1_graph.serialize(destination=str(model1_path), format="turtle")
        
        model2_path = self.test_data_dir / "model2.ttl"
        model2_graph = Graph()
        model2_graph.add((TEST.Class2, RDF.type, OWL.Class))
        model2_graph.add((TEST.Class2, RDFS.label, Literal("Class 2")))
        model2_graph.add((TEST.Class2, RDFS.comment, Literal("Second class")))
        model2_graph.add((TEST.Class2, OWL.versionInfo, Literal("1.0.0")))
        model2_graph.serialize(destination=str(model2_path), format="turtle")
        
        # Load models
        self.manager.load_model(str(model1_path))
        self.manager.load_model(str(model2_path))
        
        # Integrate models
        self.manager.integrate_models("model1", ["model2"])
        
        # Check integration result
        integrated_graph = self.manager.models["model1"]
        self.assertEqual(len(integrated_graph), 8)  # 4 triples from each model
        
    def test_save_model(self):
        """Test saving a model."""
        # Create and load a model
        model_path = self.test_data_dir / "test_model.ttl"
        model_graph = Graph()
        model_graph.add((TEST.TestClass, RDF.type, OWL.Class))
        model_graph.add((TEST.TestClass, RDFS.label, Literal("Test Class")))
        model_graph.add((TEST.TestClass, RDFS.comment, Literal("A test class")))
        model_graph.add((TEST.TestClass, OWL.versionInfo, Literal("1.0.0")))
        model_graph.serialize(destination=str(model_path), format="turtle")
        
        self.manager.load_model(str(model_path))
        
        # Save the model
        output_path = self.test_data_dir / "saved_model.ttl"
        self.manager.save_model("test_model", str(output_path))
        
        # Verify the saved model
        saved_graph = Graph()
        saved_graph.parse(str(output_path), format="turtle")
        self.assertEqual(len(saved_graph), 4)
        
    def test_version_tracking(self):
        """Test version tracking functionality."""
        # Create a model with version
        model_path = self.test_data_dir / "versioned_model.ttl"
        model_graph = Graph()
        
        # Add ontology declaration with version
        model_graph.add((TEST.VersionedModel, RDF.type, OWL.Ontology))
        model_graph.add((TEST.VersionedModel, OWL.versionInfo, Literal("2.0.0")))
        
        # Add a class
        model_graph.add((TEST.VersionedClass, RDF.type, OWL.Class))
        model_graph.add((TEST.VersionedClass, RDFS.label, Literal("Versioned Class")))
        model_graph.add((TEST.VersionedClass, RDFS.comment, Literal("A versioned class")))
        
        model_graph.serialize(destination=str(model_path), format="turtle")
        
        # Load the model
        self.manager.load_model(str(model_path))
        
        # Check version tracking
        self.assertIn("versioned_model", self.manager.versions)
        self.assertEqual(self.manager.versions["versioned_model"], "2.0.0")
        
        # Test get_model_version
        version = self.manager.get_model_version("versioned_model")
        self.assertEqual(version, "2.0.0")
        
    def test_dependency_tracking(self):
        """Test dependency tracking functionality."""
        # Create a model with dependencies
        model_path = self.test_data_dir / "dependent_model.ttl"
        model_graph = Graph()
        model_graph.add((TEST.DependentClass, RDF.type, OWL.Class))
        model_graph.add((TEST.DependentClass, RDFS.label, Literal("Dependent Class")))
        model_graph.add((TEST.DependentClass, RDFS.comment, Literal("A dependent class")))
        model_graph.add((TEST.DependentClass, OWL.versionInfo, Literal("1.0.0")))
        model_graph.add((TEST.DependentClass, OWL.imports, URIRef("http://example.org/dependency1")))
        model_graph.add((TEST.DependentClass, OWL.imports, URIRef("http://example.org/dependency2")))
        model_graph.serialize(destination=str(model_path), format="turtle")
        
        # Load the model
        self.manager.load_model(str(model_path))
        
        # Check dependency tracking
        self.assertIn("dependent_model", self.manager.dependencies)
        self.assertEqual(len(self.manager.dependencies["dependent_model"]), 2)
        
        # Test get_model_dependencies
        deps = self.manager.get_model_dependencies("dependent_model")
        self.assertEqual(len(deps), 2)
        self.assertIn("http://example.org/dependency1", deps)
        self.assertIn("http://example.org/dependency2", deps)
        
    def test_validation_pipeline(self):
        """Test validation pipeline functionality."""
        # Create a model with all required elements
        complete_model = Graph()
        complete_model.add((TEST.CompleteClass, RDF.type, OWL.Class))
        complete_model.add((TEST.CompleteClass, RDFS.label, Literal("Complete Class")))
        complete_model.add((TEST.CompleteClass, RDFS.comment, Literal("A complete class")))
        complete_model.add((TEST.CompleteClass, OWL.versionInfo, Literal("1.0.0")))
        complete_model.add((TEST.CompleteClass, OWL.imports, URIRef("http://example.org/dependency")))
        
        # Run validation pipeline
        self.manager._run_validation_pipeline(complete_model)  # Should not raise warnings
        
        # Create a model missing elements
        incomplete_model = Graph()
        incomplete_model.add((TEST.IncompleteClass, RDF.type, OWL.Class))
        
        # Run validation pipeline
        with self.assertLogs(level='WARNING') as log:
            self.manager._run_validation_pipeline(incomplete_model)
            self.assertIn("Model missing documentation", log.output[0])
            self.assertIn("Model missing version information", log.output[1])
            self.assertIn("Model missing dependency declarations", log.output[2])
            
    def test_command_line_interface(self):
        """Test command line interface functionality."""
        logger.info("Testing command line interface")
        try:
            model_path = self.test_model_path
            temp_dir = Path(self.temp_dir) / "test_data"  # Use test_data subdirectory
            output_path = temp_dir / "cli_output.ttl"
            
            # Ensure Python can find the module
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).parent.parent)
            
            # First load the model
            load_cmd = [
                sys.executable,
                "-m",
                "src.ontology_framework.manage_models",
                "--base-dir",
                str(temp_dir),
                "--load",
                str(model_path)
            ]
            
            result = subprocess.run(load_cmd, capture_output=True, text=True, env=env)
            logger.debug(f"Load command output: {result.stdout}")
            logger.debug(f"Load command error: {result.stderr}")
            self.assertEqual(result.returncode, 0, f"Load command failed with return code {result.returncode}. Error: {result.stderr}")
            
            # Then save it
            save_cmd = load_cmd + ["--save", str(output_path)]
            result = subprocess.run(save_cmd, capture_output=True, text=True, env=env)
            logger.debug(f"Save command output: {result.stdout}")
            logger.debug(f"Save command error: {result.stderr}")
            self.assertEqual(result.returncode, 0, f"Save command failed with return code {result.returncode}. Error: {result.stderr}")
            self.assertTrue(output_path.exists(), "Output file was not created")
            
            # Finally check version
            version_cmd = load_cmd + ["--version", Path(model_path).stem]
            result = subprocess.run(version_cmd, capture_output=True, text=True, env=env)
            logger.debug(f"Version command output: {result.stdout}")
            logger.debug(f"Version command error: {result.stderr}")
            self.assertEqual(result.returncode, 0, f"Version command failed with return code {result.returncode}. Error: {result.stderr}")
            self.assertIn("1.0.0", result.stdout, "Version information not found in output")
            logger.info("Command line interface test passed")
        except Exception as e:
            logger.error(f"Command line interface test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
            
    def test_model_first_principle(self):
        """Test that model quality takes precedence over code quality."""
        logger.info("Testing model-first principle")
        try:
            # Mock model quality check to fail
            with patch.object(self.manager, 'check_model_quality', return_value=False):
                with self.assertRaises(ModelQualityError) as cm:
                    self.manager.validate_system_quality(str(self.test_model_path))
                logger.debug(f"Expected ModelQualityError raised: {str(cm.exception)}")
                
            # Mock model projection check to fail
            with patch.object(self.manager, '_check_projection_alignment', return_value=False):
                with self.assertRaises(ModelProjectionError) as cm:
                    self.manager.validate_model_projection(str(self.test_model_path))
                logger.debug(f"Expected ModelProjectionError raised: {str(cm.exception)}")
            logger.info("Model-first principle test passed")
        except Exception as e:
            logger.error(f"Model-first principle test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
            
    def test_model_quality_precedence(self):
        """Test the model quality precedence principle"""
        # Mock model and code quality checks
        self.manager.check_model_quality = MagicMock(return_value=False)
        self.manager.check_code_quality = MagicMock(return_value=True)
        
        with self.assertRaises(ModelQualityError):
            self.manager.validate_system_quality(str(self.test_model_path))
            
        # Verify model quality was checked before code quality
        self.manager.check_model_quality.assert_called_once()
        self.manager.check_code_quality.assert_not_called()
        
    def test_model_projection_alignment(self):
        """Test model projection alignment validation."""
        logger.info("Testing model projection alignment")
        try:
            test_model = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix test: <http://example.org/test#> .

test:TestClass
    a owl:Class ;
    rdfs:label "Test Class" ;
    rdfs:comment "A test class" ."""
                
            test_projection = {
                "class_name": "TestClass",
                "attributes": ["label", "comment"]
            }
            
            result = self.manager.validate_projection(test_model, test_projection)
            logger.debug(f"Projection validation result: {result}")
            self.assertTrue(result)
            logger.info("Projection alignment test passed")
        except Exception as e:
            logger.error(f"Projection alignment test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
            
    def test_model_validation_pipeline(self):
        """Test the complete model validation pipeline."""
        logger.info("Testing model validation pipeline")
        try:
            # Load the model first
            self.manager.load_model(str(self.test_model_path))
            model_name = self.test_model_path.stem
            
            # Now validate by name
            result = self.manager.validate_model_quality(model_name)
            logger.debug(f"Validation pipeline result: {result}")
            self.assertTrue(result)
            logger.info("Validation pipeline test passed")
        except Exception as e:
            logger.error(f"Validation pipeline test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
            
    def test_model_documentation(self):
        """Test model documentation requirements"""
        test_model = """
        @prefix : <./test#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        
        :TestModel rdf:type owl:Ontology ;
            rdfs:label "Test Model" ;
            rdfs:comment "A test model" ;
            owl:versionInfo "1.0.0" .
        """
        
        # Test documentation validation
        self.assertTrue(
            self.manager.validate_documentation(test_model),
            "Model should have required documentation"
        )
        
    @patch('ontology_framework.manage_models.ModelManager.check_shacl_constraints')
    def test_shacl_validation(self, mock_shacl):
        """Test SHACL validation."""
        logger.info("Testing SHACL validation")
        try:
            # Configure mock
            mock_shacl.return_value = True
            
            # Load and validate model
            model_path = str(self.test_model_path)
            self.manager.load_model(model_path)
            result = self.manager.validate_model(model_path)
            
            # Verify validation was called
            mock_shacl.assert_called_once()
            self.assertTrue(result)
            logger.info("SHACL validation test passed")
        except Exception as e:
            logger.error(f"SHACL validation test failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

if __name__ == "__main__":
    unittest.main() 