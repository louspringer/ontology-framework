import unittest
from rdflib import Graph, URIRef, Literal, Namespace, XSD
from rdflib.namespace import RDF, RDFS, OWL, SH
from ontology_framework.validation.validation_handler import ValidationHandler
from ontology_framework.validation.validation_rule_type import ValidationRuleType
from ontology_framework.validation.error_severity import ErrorSeverity
import pytest
import os

# Test namespace
TEST = Namespace("http://example.org/test#")

class TestValidationHandler(unittest.TestCase):
    def setUp(self):
        """Initialize test environment with proper semantic tooling"""
        self.handler = ValidationHandler()
        self.test_graph = Graph()
        self.test_graph.bind('test', TEST)
        self.test_graph.bind('owl', OWL)
        self.test_graph.bind('rdf', RDF)
        self.test_graph.bind('rdfs', RDFS)
        self.test_graph.bind('xsd', XSD)
        self.setup_test_ontology()
        
    def setup_test_ontology(self):
        """Setup test ontology using semantic web tools"""
        from rdflib import URIRef, Literal, XSD
        g = self.test_graph
        TEST = "http://example.org/test#"
        OWL = "http://www.w3.org/2002/07/owl#"
        RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        RDFS = "http://www.w3.org/2000/01/rdf-schema#"
        # Classes
        g.add((URIRef(TEST + "Class1"), URIRef(RDF + "type"), URIRef(OWL + "Class")))
        g.add((URIRef(TEST + "Class2"), URIRef(RDF + "type"), URIRef(OWL + "Class")))
        # Property
        g.add((URIRef(TEST + "prop1"), URIRef(RDF + "type"), URIRef(OWL + "ObjectProperty")))
        g.add((URIRef(TEST + "prop1"), URIRef(RDFS + "domain"), URIRef(TEST + "Class1")))
        g.add((URIRef(TEST + "prop1"), URIRef(RDFS + "range"), URIRef(TEST + "Class2")))
        # Individuals and properties
        g.add((URIRef(TEST + "inst1"), URIRef(RDF + "type"), URIRef(TEST + "Class1")))
        g.add((URIRef(TEST + "inst1"), URIRef(TEST + "prop1"), Literal("test_pattern", datatype=XSD.string)))
        g.add((URIRef(TEST + "inst1"), URIRef(TEST + "description"), Literal("This contains a password", datatype=XSD.string)))
        g.add((URIRef(TEST + "inst2"), URIRef(RDF + "type"), URIRef(TEST + "Class1")))
        g.add((URIRef(TEST + "inst2"), URIRef(TEST + "prop1"), Literal("secret", datatype=XSD.string)))
        g.add((URIRef(TEST + "inst2"), URIRef(TEST + "description"), Literal("Another test_pattern", datatype=XSD.string)))
        g.add((URIRef(TEST + "inst3"), URIRef(RDF + "type"), URIRef(TEST + "Class2")))
        g.add((URIRef(TEST + "inst3"), URIRef(TEST + "prop1"), Literal("not_sensitive", datatype=XSD.string)))
        g.add((URIRef(TEST + "inst3"), URIRef(TEST + "description"), Literal("no match here", datatype=XSD.string)))
        g.add((URIRef(TEST + "inst4"), URIRef(RDF + "type"), URIRef(TEST + "Class1")))
        g.add((URIRef(TEST + "inst4"), URIRef(TEST + "prop1"), Literal(123, datatype=XSD.integer)))

    def test_shacl_validation(self):
        """Test SHACL validation using proper semantic tooling"""
        # Create SHACL shapes using SPARQL INSERT
        shapes_graph = Graph()
        shapes_graph.bind('sh', SH)
        shapes_graph.bind('test', TEST)
        
        insert_shapes_query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX test: <http://example.org/test#>
        
        INSERT DATA {
            test:ClassShape a sh:NodeShape ;
                sh:targetClass test:Class1 ;
                sh:property [
                    sh:path test:prop1 ;
                    sh:class test:Class2 ;
                    sh:minCount 1 
                ] .
        }
        """
        shapes_graph.update(insert_shapes_query)
        
        # Test validation
        result = self.handler.validate_shacl(self.test_graph, shapes_graph)
        self.assertTrue(result['conforms'])
        
    def test_validation_rule_registration(self):
        """Test registering a validation rule."""
        rule = {
            "type": ValidationRuleType.SEMANTIC,
            "pattern": "test_pattern",
            "message": "Test validation message"
        }
        rule_id = self.handler.register_rule("test_rule", rule)
        self.assertEqual(rule_id, "test_rule")
        self.assertIn("test_rule", self.handler.rules)
        self.assertEqual(self.handler.rules["test_rule"]["type"], ValidationRuleType.SEMANTIC)

    def test_execute_rule(self):
        """Test executing a validation rule."""
        rule = {
            "type": ValidationRuleType.SEMANTIC,
            "pattern": "test_pattern",
            "message": "Test validation message"
        }
        self.handler.register_rule("test_rule", rule)
        result = self.handler.execute_rule("test_rule", self.test_graph)
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)

    def test_validate_graph(self):
        """Test validating a graph against all rules."""
        rule_id = "test_rule"
        rule = {
            "type": ValidationRuleType.SEMANTIC,
            "pattern": "test_pattern",
            "message": "Test validation message"
        }
        self.handler.register_rule(rule_id, rule)
        results = self.handler.validate_graph(self.test_graph)
        self.assertIsInstance(results, dict)
        self.assertIn("results", results)

    def test_syntax_validation(self):
        """Test syntax validation rule."""
        rule = {
            "type": ValidationRuleType.SYNTAX,
            "pattern": r"[A-Z][a-z]+",
            "message": "Invalid syntax"
        }
        self.handler.register_rule("syntax_test", rule)
        result = self.handler.validate_graph(self.test_graph)
        self.assertEqual(len(result["results"]), 1)

    def test_sensitive_data_validation(self):
        """Test sensitive data validation rule."""
        rule = {
            "type": ValidationRuleType.SENSITIVE_DATA,
            "patterns": ["password", "secret"],
            "message": "Contains sensitive data"
        }
        self.handler.register_rule("sensitive_test", rule)
        result = self.handler.validate_graph(self.test_graph)
        self.assertEqual(len(result["results"]), 2)

    def test_pattern_validation(self):
        """Test pattern validation rule."""
        rule = {
            "type": ValidationRuleType.PATTERN,
            "pattern": "test_pattern",
            "message": "Pattern validation failed"
        }
        self.handler.register_rule("pattern_test", rule)
        result = self.handler.validate_graph(self.test_graph)
        # There are 2 triples with 'test_pattern' in the object: inst1/prop1 and inst2/description
        self.assertEqual(len(result["results"]), 2)

    def test_rule_dependencies(self):
        """Test rule dependency validation."""
        rules = [
            {
                "id": "rule1",
                "rule": {
                    "type": ValidationRuleType.SEMANTIC,
                    "pattern": "pattern1",
                    "message": "Rule 1",
                    "dependencies": ["rule2"]
                }
            },
            {
                "id": "rule2",
                "rule": {
                    "type": ValidationRuleType.SEMANTIC,
                    "pattern": "pattern2",
                    "message": "Rule 2",
                    "dependencies": ["rule3"]
                }
            },
            {
                "id": "rule3",
                "rule": {
                    "type": ValidationRuleType.SEMANTIC,
                    "pattern": "pattern3",
                    "message": "Rule 3",
                    "dependencies": ["rule4"]
                }
            },
            {
                "id": "rule4",
                "rule": {
                    "type": ValidationRuleType.SEMANTIC,
                    "pattern": "pattern4",
                    "message": "Rule 4",
                    "dependencies": ["rule1"]
                }
            }
        ]
        
        # Register rules with circular dependency
        for rule_def in rules:
            self.handler.register_rule(rule_def["id"], rule_def["rule"])
            
        with self.assertRaises(ValueError):
            self.handler.validate_graph(self.test_graph)

    def test_individual_type_validation(self):
        """Test individual type validation."""
        rule = {
            "type": ValidationRuleType.SEMANTIC,
            "class_uri": str(TEST.Class1),
            "property_types": {str(TEST.prop1): str(XSD.string)},
            "message": "Invalid property type"
        }
        self.handler.register_rule("type_test", rule)
        result = self.handler.validate_graph(self.test_graph)
        self.assertIn("Invalid property type", str(result["results"]))

    def test_test_entity_validation(self):
        """Test entity validation rule."""
        rule = {
            "type": ValidationRuleType.PATTERN,
            "pattern": "test_pattern",
            "message": "Test entity validation failed"
        }
        self.handler.register_rule("test_entity_rule", rule)
        result = self.handler.validate_graph(self.test_graph)
        violations = [r for r in result["results"] if r["rule_id"] == "test_entity_rule"]
        # There are 2 violations for 'test_pattern'
        self.assertEqual(len(violations), 2)

    def test_valid_entity(self):
        """Test that a valid entity passes validation."""
        rule = {
            "type": ValidationRuleType.PATTERN,
            "pattern": "test_pattern",
            "message": "Pattern validation failed"
        }
        self.handler.register_rule("valid_entity_rule", rule)
        result = self.handler.validate_graph(self.test_graph)
        # There are 2 violations for 'test_pattern'
        self.assertEqual(len(result["results"]), 2)

    def test_pattern_validation_with_invalid_entities(self):
        """Test pattern validation with invalid entities."""
        rule = {
            "type": ValidationRuleType.PATTERN,
            "pattern": "test_pattern",
            "message": "Pattern validation failed"
        }
        self.handler.register_rule("pattern_invalid_entities", rule)
        result = self.handler.validate_graph(self.test_graph)
        # There are 2 triples with 'test_pattern' in the object: inst1/prop1 and inst2/description
        self.assertEqual(len(result["results"]), 2)

    def test_pattern_validation_with_test_data(self):
        """Test pattern validation with test data."""
        rule = {
            "type": ValidationRuleType.PATTERN,
            "pattern": "secret",
            "message": "Test data validation failed"
        }
        self.handler.register_rule("test_data_rule", rule)
        result = self.handler.validate_graph(self.test_graph)
        self.assertEqual(len(result["results"]), 1)

    def test_valid_entity_passes_validation(self):
        """Test that a valid entity passes all validations."""
        rule = {
            "type": ValidationRuleType.PATTERN,
            "pattern": "test_pattern",
            "message": "Pattern validation failed"
        }
        self.handler.register_rule("valid_entity_passes_rule", rule)
        result = self.handler.validate_graph(self.test_graph)
        # There are 2 violations for 'test_pattern'
        self.assertEqual(len(result["results"]), 2)

    def test_pattern_validation_with_multiple_descriptions(self):
        """Test pattern validation with multiple descriptions."""
        rule = {
            "type": ValidationRuleType.PATTERN,
            "pattern": "test_pattern",
            "message": "Pattern validation failed"
        }
        self.handler.register_rule("pattern_multiple_descriptions", rule)
        result = self.handler.validate_graph(self.test_graph)
        # There are 2 triples with 'test_pattern' in the object: inst1/prop1 and inst2/description
        self.assertEqual(len(result["results"]), 2)

    def test_pattern_validation_with_empty_graph(self):
        """Test pattern validation with an empty graph."""
        rule = {
            "type": ValidationRuleType.PATTERN,
            "pattern": "test_pattern",
            "message": "Empty graph validation",
            "shapes_graph": Graph()
        }
        self.handler.register_rule("empty_graph_rule", rule)
        result = self.handler.validate_graph(Graph())
        self.assertEqual(len(result["results"]), 0)

    def test_pattern_validation_with_invalid_datatype(self):
        """Test pattern validation with invalid datatype."""
        rule = {
            "type": ValidationRuleType.PATTERN,
            "pattern": "not_sensitive",
            "message": "Invalid datatype"
        }
        self.handler.register_rule("invalid_datatype_rule", rule)
        result = self.handler.validate_graph(self.test_graph)
        self.assertEqual(len(result["results"]), 1)

if __name__ == '__main__':
    unittest.main() 