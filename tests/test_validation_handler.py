import os
import tempfile
from unittest import TestCase
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, SH
from pyshacl import validate as pyshacl_validate

from src.ontology_framework.validation.validation_handler import ValidationHandler
from src.ontology_framework.validation.conformance_level import ConformanceLevel
from src.ontology_framework.validation.validation_rule_type import ValidationRuleType

class TestValidationHandler(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.guidance_file = os.path.join(self.temp_dir, "test_guidance.ttl")
        
        # Create test guidance ontology with validation rules using RDFlib
        guidance = Graph()
        ex = Namespace("http://example.org/")
        guidance.bind("ex", ex)
        
        # Add test rules using RDFlib
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
        
        # Serialize using RDFlib
        guidance.serialize(self.guidance_file, format="turtle")
        
        # Initialize ValidationHandler with test rules
        self.handler = ValidationHandler()
        self.handler.register_rule(
            rule_id="TestRule",
            rule={"pattern": "[A-Z][a-z]+"},
            conformance_level=ConformanceLevel.STRICT,
            priority=1
        )
        self.handler.register_rule(
            rule_id="SensitiveRule",
            rule={"pattern": "password|secret|key"},
            conformance_level=ConformanceLevel.STRICT,
            rule_type=ValidationRuleType.SENSITIVE_DATA,
            priority=1
        )

    def test_load_validation_rules(self):
        """Test loading validation rules from guidance ontology."""
        # Load guidance ontology using RDFlib
        guidance = Graph()
        guidance.parse(self.guidance_file, format="turtle")
        
        # Query rules using SPARQL
        query = """
        SELECT ?rule ?type ?pattern
        WHERE {
            ?rule a ex:ValidationRule .
            ?rule ex:ruleType ?type .
            ?rule ex:pattern ?pattern .
        }
        """
        results = guidance.query(query)
        
        # Verify rules were loaded
        self.assertEqual(len(list(results)), 2)
        
    def test_validate_syntax(self):
        """Test syntax validation."""
        # Create test graph using RDFlib
        test_graph = Graph()
        test_graph.add((URIRef("http://example.org/Test"), RDFS.label, Literal("ValidName")))
        
        # Validate using SHACL
        conforms, _, _ = pyshacl_validate(
            test_graph,
            shacl_graph=self.handler.get_shacl_rules(),
            inference="rdfs",
            abort_on_first=False,
            meta_shacl=False,
            debug=False
        )
        
        self.assertTrue(conforms)
        
    def test_validate_sensitive_data(self):
        """Test sensitive data validation."""
        # Create test graph using RDFlib
        test_graph = Graph()
        test_graph.add((URIRef("http://example.org/Test"), RDFS.label, Literal("password123")))
        
        # Validate using SHACL
        conforms, _, _ = pyshacl_validate(
            test_graph,
            shacl_graph=self.handler.get_shacl_rules(),
            inference="rdfs",
            abort_on_first=False,
            meta_shacl=False,
            debug=False
        )
        
        self.assertFalse(conforms)
        
    def test_validate_graph(self):
        """Test full graph validation."""
        # Create test graph using RDFlib
        test_graph = Graph()
        test_graph.add((URIRef("http://example.org/Test"), RDFS.label, Literal("ValidName")))
        test_graph.add((URIRef("http://example.org/Test"), RDFS.comment, Literal("No sensitive data")))
        
        # Validate using handler
        result = self.handler.validate(test_graph)
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertTrue(result["valid"])
        
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.guidance_file):
            os.remove(self.guidance_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir) 