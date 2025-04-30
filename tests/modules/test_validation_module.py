"""Tests for the validation module."""

import unittest
from rdflib import Graph
from ontology_framework.modules.validation import ValidationModule

class TestValidationModule(unittest.TestCase):
    """Test cases for the validation module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_graph = Graph()
        self.test_graph.parse("tests/fixtures/test_ontologies/ontology_types.ttl", format="turtle")
        
        self.shapes_graph = Graph()
        self.shapes_graph.parse("tests/fixtures/test_ontologies/ontology_types_shapes.ttl", format="turtle")
        
        self.validation_module = ValidationModule(self.test_graph, self.shapes_graph)
        
    def test_validate(self):
        """Test the validate method."""
        results = self.validation_module.validate()
        
        self.assertIn("conforms", results)
        self.assertIn("results_graph", results)
        self.assertIn("results_text", results)
        self.assertIsInstance(results["conforms"], bool)
        self.assertIsInstance(results["results_graph"], Graph)
        self.assertIsInstance(results["results_text"], str)
        
    def test_validate_no_graph(self):
        """Test validation with no graph."""
        module = ValidationModule()
        with self.assertRaises(ValueError):
            module.validate()
            
    def test_validate_no_shapes(self):
        """Test validation with no shapes graph."""
        module = ValidationModule(self.test_graph)
        with self.assertRaises(ValueError):
            module.validate()
            
    def test_get_requirements(self):
        """Test the get_requirements method."""
        requirements = self.validation_module.get_requirements()
        
        self.assertIn("shapes_graph", requirements)
        self.assertIn("data_graph", requirements)
        self.assertEqual(requirements["shapes_graph"], "SHACL shapes graph for validation")
        self.assertEqual(requirements["data_graph"], "RDF graph to validate")
        
    def test_set_shapes_graph(self):
        """Test the set_shapes_graph method."""
        new_shapes = Graph()
        new_shapes.parse("tests/fixtures/test_ontologies/ontology_types_shapes.ttl", format="turtle")
        
        self.validation_module.set_shapes_graph(new_shapes)
        self.assertEqual(self.validation_module.shapes_graph, new_shapes) 