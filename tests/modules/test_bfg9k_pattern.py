"""Tests for the BFG9K validation pattern."""

import unittest
from rdflib import Graph, URIRef
from ontology_framework.modules.validation import BFG9KPattern, BFG9KValidationResult

class TestBFG9KPattern(unittest.TestCase):
    """Test cases for the BFG9K validation pattern."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_graph = Graph()
        self.test_graph.parse("tests/fixtures/test_ontologies/ontology_types.ttl", format="turtle")
        self.pattern = BFG9KPattern(self.test_graph)
        
    def test_validate(self):
        """Test the validate method."""
        result = self.pattern.validate()
        
        self.assertIsInstance(result, BFG9KValidationResult)
        self.assertIsInstance(result.conforms, bool)
        self.assertIsInstance(result.violations, list)
        self.assertIsInstance(result.focus_nodes, list)
        self.assertIsInstance(result.severity, str)
        self.assertIsInstance(result.message, str)
        
    def test_validate_no_graph(self):
        """Test validation with no graph."""
        pattern = BFG9KPattern()
        with self.assertRaises(ValueError):
            pattern.validate()
            
    def test_set_graph(self):
        """Test setting a new graph."""
        new_graph = Graph()
        new_graph.parse("tests/fixtures/test_ontologies/ontology_types.ttl", format="turtle")
        
        self.pattern.set_graph(new_graph)
        self.assertEqual(self.pattern.graph, new_graph)
        
    def test_validation_result_structure(self):
        """Test the structure of validation results."""
        result = BFG9KValidationResult(
            conforms=True,
            violations=[],
            focus_nodes=[],
            severity="info",
            message="Test validation"
        )
        
        self.assertTrue(result.conforms)
        self.assertEqual(result.violations, [])
        self.assertEqual(result.focus_nodes, [])
        self.assertEqual(result.severity, "info")
        self.assertEqual(result.message, "Test validation")
