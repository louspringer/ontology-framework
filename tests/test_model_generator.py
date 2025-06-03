"""Tests for the model generator."""

import unittest
from pathlib import Path
from rdflib import Graph, URIRef, Literal
from ontology_framework.tools.model_generator import ModelGenerator

class TestModelGenerator(unittest.TestCase):
    """Test cases for model generator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = ModelGenerator()
        self.test_file = Path(__file__).parent / "test_data" / "test_module.py"
        self.test_graph = Graph()
        self.test_uri = URIRef("http://example.org/test")
        self.test_literal = Literal("test value")
        
    def test_analyze_file(self):
        """Test analyzing a Python file."""
        with open(self.test_file, "w") as f:
            f.write('''
class TestClass:
    """Test class docstring."""
    def test_method(self):
        """Test method docstring."""
        pass
''')
        
        analysis = self.generator.analyze_file(self.test_file)
        self.assertIn("TestClass", analysis["classes"])
        self.assertIn("test_method", analysis["functions"])
        
    def test_generator_initialization(self):
        """Test generator initialization."""
        self.assertIsNotNone(self.generator)
        self.assertEqual(len(self.generator.models), 0)

    def test_add_model(self):
        """Test adding a model."""
        self.generator.add_model(self.test_graph)
        self.assertEqual(len(self.generator.models), 1)
        self.assertIn(self.test_graph, self.generator.models)

    def test_generate_model(self):
        """Test model generation."""
        self.test_graph.add((self.test_uri, URIRef("http://example.org/property"), self.test_literal))
        self.generator.add_model(self.test_graph)
        
        generated_model = self.generator.generate()
        self.assertIsNotNone(generated_model)
        self.assertTrue(isinstance(generated_model, Graph))
        self.assertGreater(len(generated_model), 0)

    def test_merge_models(self):
        """Test model merging."""
        graph1 = Graph()
        graph2 = Graph()
        
        graph1.add((self.test_uri, URIRef("http://example.org/prop1"), Literal("value1")))
        graph2.add((self.test_uri, URIRef("http://example.org/prop2"), Literal("value2")))
        
        self.generator.add_model(graph1)
        self.generator.add_model(graph2)
        
        merged_model = self.generator.merge_models()
        self.assertEqual(len(merged_model), 2)

    def test_validate_model(self):
        """Test model validation."""
        self.test_graph.add((self.test_uri, URIRef("http://example.org/property"), self.test_literal))
        validation_result = self.generator.validate_model(self.test_graph)
        self.assertTrue(validation_result.is_valid)
        self.assertEqual(len(validation_result.errors), 0)

    def test_invalid_model(self):
        """Test invalid model handling."""
        invalid_graph = "not a graph"
        with self.assertRaises(ValueError):
            self.generator.validate_model(invalid_graph)

    def test_save_models(self):
        """Test saving models to a file."""
        model = self.generator.generate_model(self.test_file)
        output_file = Path(__file__).parent / "test_data" / "test_models.ttl"
        self.generator.save_models(output_file)
        
        # Verify file exists and contains triples
        self.assertTrue(output_file.exists())
        loaded_graph = Graph()
        loaded_graph.parse(output_file, format="turtle")
        self.assertTrue(len(loaded_graph) > 0)

    def tearDown(self):
        """Clean up test files."""
        if self.test_file.exists():
            self.test_file.unlink()
        test_models = Path(__file__).parent / "test_data" / "test_models.ttl"
        if test_models.exists():
            test_models.unlink()
        self.generator = None
        self.test_graph = None
        self.test_uri = None
        self.test_literal = None
            
if __name__ == "__main__":
    unittest.main() 