import os
import tempfile
from unittest import TestCase
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS

from src.ontology_framework.validation.validation_handler import ValidationHandler
from src.ontology_framework.ontology_types import ValidationRuleType

class TestValidationHandler(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.guidance_file = os.path.join(self.temp_dir, "test_guidance.ttl")
        
        # Create test guidance ontology with validation rules
        guidance = Graph()
        ex = Namespace("http://example.org/")
        guidance.bind("ex", ex)
        
        # Add test rules
        rule1 = ex["TestRule"]
        guidance.add((rule1, RDF.type, ex.ValidationRule))
        guidance.add((rule1, RDFS.label, Literal("Test Rule")))
        guidance.add((rule1, ex.ruleType, Literal("SYNTAX")))
        guidance.add((rule1, ex.pattern, Literal("[A-Z][a-z]+")))
        
        rule2 = ex["SensitiveRule"]
        guidance.add((rule2, RDF.type, ex.ValidationRule))
        guidance.add((rule2, RDFS.label, Literal("Sensitive Data Rule")))
        guidance.add((rule2, ex.ruleType, Literal("SENSITIVE_DATA")))
        guidance.add((rule2, ex.pattern, Literal("password|secret|key")))
        
        guidance.serialize(self.guidance_file, format="turtle")
        
        # Initialize ValidationHandler with test rules
        self.handler = ValidationHandler()
        self.handler.register_rule(
            "TestRule",
            ValidationRuleType.SYNTAX,
            pattern="[A-Z][a-z]+",
            priority=1
        )
        self.handler.register_rule(
            "SensitiveRule",
            ValidationRuleType.SENSITIVE_DATA,
            pattern="password|secret|key",
            priority=1
        )

    def test_load_validation_rules(self):
        """Test that validation rules are loaded from guidance ontology"""
        self.assertGreaterEqual(len(self.handler.rules), 2)
        test_rule = self.handler.rules.get("TestRule")
        self.assertIsNotNone(test_rule)
        self.assertEqual(test_rule["type"], ValidationRuleType.SYNTAX)

    def test_validate_syntax(self):
        """Test syntax validation with a pattern rule"""
        test_graph = Graph()
        ex = Namespace("http://example.org/")
        test_graph.add((ex.test, RDFS.label, Literal("invalid_name")))
        
        result = self.handler.execute_rule("TestRule", test_graph)
        self.assertFalse(result["is_valid"])
        self.assertEqual(len(result["violations"]), 1)

    def test_validate_sensitive_data(self):
        """Test sensitive data validation"""
        test_graph = Graph()
        ex = Namespace("http://example.org/")
        test_graph.add((ex.config, ex.password, Literal("secret123")))
        
        result = self.handler.execute_rule("SensitiveRule", test_graph)
        self.assertFalse(result["is_valid"])
        self.assertEqual(len(result["violations"]), 1)

    def test_validate_graph(self):
        """Test validation of entire graph with multiple rules"""
        test_graph = Graph()
        ex = Namespace("http://example.org/")
        test_graph.add((ex.config, ex.password, Literal("secret123")))
        test_graph.add((ex.test, RDFS.label, Literal("invalid_name")))
        
        result = self.handler.validate_graph(test_graph)
        self.assertFalse(result["is_valid"])
        self.assertGreaterEqual(len(result["violations"]), 2)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir) 