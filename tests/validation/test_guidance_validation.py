import unittest
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS
import pyshacl
from ontology_framework.validation.validation_handler import ValidationHandler
from ontology_framework.model.model_manager import ModelManager

class TestGuidanceValidation(unittest.TestCase):
    def setUp(self):
        self.guidance_graph = Graph()
        self.guidance_graph.parse("tests/fixtures/test_ontologies/guidance_test.ttl", format="turtle")
        
        self.shapes_graph = Graph()
        self.shapes_graph.parse("tests/fixtures/test_ontologies/guidance_test_shapes.ttl", format="turtle")
        
        self.validation_handler = ValidationHandler()
        self.model_manager = ModelManager()

    def test_shacl_validation(self):
        """Test SHACL validation of guidance ontology"""
        conforms, results_graph, results_text = pyshacl.validate(
            self.guidance_graph,
            shacl_graph=self.shapes_graph,
            ont_graph=None,
            inference='rdfs',
            abort_on_first=False,
            allow_warnings=False,
            meta_shacl=False,
            advanced=True,
            js=False,
            debug=False
        )
        self.assertTrue(conforms, f"SHACL validation failed: {results_text}")

    def test_conformance_levels(self):
        """Test conformance level validation"""
        conformance_levels = list(self.guidance_graph.subjects(RDF.type, URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#ConformanceLevel")))
        self.assertEqual(len(conformance_levels), 3, "Expected 3 conformance levels")
        
        # Test each conformance level has required properties
        for level in conformance_levels:
            label = self.guidance_graph.value(level, RDFS.label)
            comment = self.guidance_graph.value(level, RDFS.comment)
            self.assertIsNotNone(label, f"Missing label for {level}")
            self.assertIsNotNone(comment, f"Missing comment for {level}")

    def test_validation_rules(self):
        """Test validation rule implementation"""
        rules = list(self.guidance_graph.subjects(RDF.type, URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#ValidationRule")))
        self.assertEqual(len(rules), 4, "Expected 4 validation rules")
        
        for rule in rules:
            # Test required properties
            label = self.guidance_graph.value(rule, RDFS.label)
            comment = self.guidance_graph.value(rule, RDFS.comment)
            message = self.guidance_graph.value(rule, URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#hasMessage"))
            priority = self.guidance_graph.value(rule, URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#hasPriority"))
            target = self.guidance_graph.value(rule, URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#hasTarget"))
            validator = self.guidance_graph.value(rule, URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#hasValidator"))
            
            self.assertIsNotNone(label, f"Missing label for {rule}")
            self.assertIsNotNone(comment, f"Missing comment for {rule}")
            self.assertIsNotNone(message, f"Missing message for {rule}")
            self.assertIsNotNone(priority, f"Missing priority for {rule}")
            self.assertIsNotNone(target, f"Missing target for {rule}")
            self.assertIsNotNone(validator, f"Missing validator for {rule}")

    def test_model_manager_validation(self):
        """Test model manager validation methods"""
        # Test SPORE validation
        spore_result = self.model_manager.validate_spore(self.guidance_graph)
        self.assertIsNotNone(spore_result)
        self.assertTrue(isinstance(spore_result, dict))
        
        # Test semantic validation
        semantic_result = self.model_manager.validate_semantic(self.guidance_graph)
        self.assertIsNotNone(semantic_result)
        self.assertTrue(isinstance(semantic_result, dict))
        
        # Test syntax validation
        syntax_result = self.model_manager.validate_syntax(self.guidance_graph)
        self.assertIsNotNone(syntax_result)
        self.assertTrue(isinstance(syntax_result, dict))
        
        # Test consistency validation
        consistency_result = self.model_manager.validate_consistency(self.guidance_graph)
        self.assertIsNotNone(consistency_result)
        self.assertTrue(isinstance(consistency_result, dict))

    def test_validation_handler(self):
        """Test validation handler integration"""
        # Test rule registration
        self.validation_handler.register_rule(self.guidance_graph)
        registered_rules = self.validation_handler.get_registered_rules()
        self.assertEqual(len(registered_rules), 4, "Expected 4 registered rules")
        
        # Test rule execution
        for rule in registered_rules:
            result = self.validation_handler.execute_rule(rule, self.guidance_graph)
            self.assertIsNotNone(result)
            self.assertTrue(isinstance(result, dict))
            self.assertIn("conforms", result)
            self.assertIn("results", result)

if __name__ == '__main__':
    unittest.main()
