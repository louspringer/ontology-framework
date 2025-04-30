import unittest
from rdflib import Graph
from pyshacl import validate
import os

class TestOntologyTypes(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.fixtures_dir = os.path.join(self.test_dir, '..', 'fixtures', 'test_ontologies')
        
        # Load test ontology
        self.ontology = Graph()
        self.ontology.parse(
            os.path.join(self.fixtures_dir, 'ontology_types.ttl'),
            format='turtle'
        )
        
        # Load SHACL shapes
        self.shapes = Graph()
        self.shapes.parse(
            os.path.join(self.fixtures_dir, 'ontology_types_shapes.ttl'),
            format='turtle'
        )

    def test_validation_rule_types(self):
        """Test validation of ValidationRuleType instances"""
        conforms, results_graph, results_text = validate(
            self.ontology,
            shacl_graph=self.shapes,
            ont_graph=None,
            inference='rdfs',
            abort_on_first=False,
            allow_warnings=False,
            meta_shacl=False,
            debug=False
        )
        self.assertTrue(conforms, f"Validation failed: {results_text}")

    def test_error_severity_levels(self):
        """Test validation of ErrorSeverity instances"""
        conforms, results_graph, results_text = validate(
            self.ontology,
            shacl_graph=self.shapes,
            ont_graph=None,
            inference='rdfs',
            abort_on_first=False,
            allow_warnings=False,
            meta_shacl=False,
            debug=False
        )
        self.assertTrue(conforms, f"Validation failed: {results_text}")

    def test_compliance_levels(self):
        """Test validation of ComplianceLevel instances"""
        conforms, results_graph, results_text = validate(
            self.ontology,
            shacl_graph=self.shapes,
            ont_graph=None,
            inference='rdfs',
            abort_on_first=False,
            allow_warnings=False,
            meta_shacl=False,
            debug=False
        )
        self.assertTrue(conforms, f"Validation failed: {results_text}")

if __name__ == '__main__':
    unittest.main() 