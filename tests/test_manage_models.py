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
from src.ontology_framework.manage_models import ModelManager

# Test namespaces
TEST = Namespace("http://example.org/test#")

class TestModelManager(unittest.TestCase):
    """Test cases for the ModelManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        
        # Create a minimal guidance ontology
        self.guidance_path = self.base_dir / "guidance.ttl"
        guidance_graph = Graph()
        guidance_graph.add((TEST.Guidance, RDF.type, OWL.Ontology))
        guidance_graph.add((TEST.Guidance, RDFS.label, Literal("Guidance Ontology")))
        guidance_graph.add((TEST.Guidance, RDFS.comment, Literal("Test guidance ontology")))
        guidance_graph.add((TEST.Guidance, OWL.versionInfo, Literal("1.0.0")))
        guidance_graph.serialize(destination=str(self.guidance_path), format="turtle")
        
        self.manager = ModelManager(str(self.base_dir))
        
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
        
    def test_initialization(self):
        """Test ModelManager initialization."""
        self.assertIsInstance(self.manager, ModelManager)
        self.assertEqual(self.manager.base_dir, self.base_dir)
        self.assertIsInstance(self.manager.guidance_graph, Graph)
        self.assertEqual(len(self.manager.models), 0)
        self.assertEqual(len(self.manager.versions), 0)
        self.assertEqual(len(self.manager.dependencies), 0)
        
    def test_load_valid_model(self):
        """Test loading a valid model."""
        # Create a valid test model
        model_path = self.base_dir / "test_model.ttl"
        model_graph = Graph()
        model_graph.add((TEST.TestClass, RDF.type, OWL.Class))
        model_graph.add((TEST.TestClass, RDFS.label, Literal("Test Class")))
        model_graph.add((TEST.TestClass, RDFS.comment, Literal("A test class")))
        model_graph.add((TEST.TestClass, OWL.versionInfo, Literal("1.0.0")))
        model_graph.serialize(destination=str(model_path), format="turtle")
        
        # Load the model
        loaded_graph = self.manager.load_model(str(model_path))
        self.assertIsInstance(loaded_graph, Graph)
        self.assertEqual(len(loaded_graph), 4)
        self.assertIn("test_model", self.manager.models)
        self.assertIn("test_model", self.manager.versions)
        self.assertEqual(self.manager.versions["test_model"], "1.0.0")
        
    def test_load_invalid_model(self):
        """Test loading an invalid model."""
        # Create an invalid test model (missing required properties)
        model_path = self.base_dir / "invalid_model.ttl"
        model_graph = Graph()
        model_graph.add((TEST.InvalidClass, RDF.type, OWL.Class))
        model_graph.serialize(destination=str(model_path), format="turtle")
        
        # Attempt to load the model
        with self.assertRaises(ValueError):
            self.manager.load_model(str(model_path))
            
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
        model1_path = self.base_dir / "model1.ttl"
        model1_graph = Graph()
        model1_graph.add((TEST.Class1, RDF.type, OWL.Class))
        model1_graph.add((TEST.Class1, RDFS.label, Literal("Class 1")))
        model1_graph.add((TEST.Class1, RDFS.comment, Literal("First class")))
        model1_graph.add((TEST.Class1, OWL.versionInfo, Literal("1.0.0")))
        model1_graph.serialize(destination=str(model1_path), format="turtle")
        
        model2_path = self.base_dir / "model2.ttl"
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
        model_path = self.base_dir / "test_model.ttl"
        model_graph = Graph()
        model_graph.add((TEST.TestClass, RDF.type, OWL.Class))
        model_graph.add((TEST.TestClass, RDFS.label, Literal("Test Class")))
        model_graph.add((TEST.TestClass, RDFS.comment, Literal("A test class")))
        model_graph.add((TEST.TestClass, OWL.versionInfo, Literal("1.0.0")))
        model_graph.serialize(destination=str(model_path), format="turtle")
        
        self.manager.load_model(str(model_path))
        
        # Save the model
        output_path = self.base_dir / "saved_model.ttl"
        self.manager.save_model("test_model", str(output_path))
        
        # Verify the saved model
        saved_graph = Graph()
        saved_graph.parse(str(output_path), format="turtle")
        self.assertEqual(len(saved_graph), 4)
        
    def test_version_tracking(self):
        """Test version tracking functionality."""
        # Create a model with version
        model_path = self.base_dir / "versioned_model.ttl"
        model_graph = Graph()
        model_graph.add((TEST.VersionedClass, RDF.type, OWL.Class))
        model_graph.add((TEST.VersionedClass, RDFS.label, Literal("Versioned Class")))
        model_graph.add((TEST.VersionedClass, RDFS.comment, Literal("A versioned class")))
        model_graph.add((TEST.VersionedClass, OWL.versionInfo, Literal("2.0.0")))
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
        model_path = self.base_dir / "dependent_model.ttl"
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
        """Test the command line interface."""
        import subprocess
        import sys
        
        # Create a test model
        model_path = self.base_dir / "cli_test.ttl"
        model_graph = Graph()
        model_graph.add((TEST.CliClass, RDF.type, OWL.Class))
        model_graph.add((TEST.CliClass, RDFS.label, Literal("CLI Test Class")))
        model_graph.add((TEST.CliClass, RDFS.comment, Literal("A CLI test class")))
        model_graph.add((TEST.CliClass, OWL.versionInfo, Literal("1.0.0")))
        model_graph.serialize(destination=str(model_path), format="turtle")
        
        # Test loading and saving
        output_path = self.base_dir / "cli_output.ttl"
        cmd = [
            sys.executable,
            "-m",
            "src.ontology_framework.manage_models",
            "--base-dir",
            str(self.base_dir),
            "--load",
            str(model_path),
            "--save",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(output_path.exists())
        
        # Test version command
        version_cmd = cmd[:-2] + ["--version", "cli_test"]
        result = subprocess.run(version_cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("1.0.0", result.stdout)
        
if __name__ == "__main__":
    unittest.main() 