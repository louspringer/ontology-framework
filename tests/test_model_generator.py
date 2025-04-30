"""Tests for the model generator."""

import unittest
from pathlib import Path
from rdflib import Graph, URIRef, Literal
from ontology_framework.tools.model_generator import ModelGenerator

class TestModelGenerator(unittest.TestCase):
    """Test cases for ModelGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ModelGenerator()
        self.test_file = Path(__file__).parent / "test_data" / "test_module.py"
        
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
        
    def test_generate_model(self):
        """Test generating a model from a Python file."""
        model = self.generator.generate_model(self.test_file)
        self.assertIsInstance(model, Graph)
        
        # Check class exists in model
        class_uri = URIRef(f"{self.generator.namespace}TestClass")
        self.assertIn((class_uri, None, None), model)
        
        # Check method exists in model
        method_uri = URIRef(f"{self.generator.namespace}test_method")
        self.assertIn((method_uri, None, None), model)
        
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
            
if __name__ == "__main__":
    unittest.main() 