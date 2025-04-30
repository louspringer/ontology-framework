import unittest
from pathlib import Path
from rdflib import Graph, URIRef, Namespace
from pyshacl import validate
from src.ontology_framework.ontology_types import (
    ValidationRuleType,
    PatchType,
    PatchStatus,
    ErrorSeverity,
    ErrorType,
    ErrorStep,
    ValidationRule,
    RiskLevel,
    ComplianceLevel,
    SecurityLevel,
    PerformanceMetric
)

class TestOntologyTypes(unittest.TestCase):
    def setUp(self):
        self.base_path = Path(__file__).parent.parent.parent.parent
        self.ontology_file = self.base_path / "tests/fixtures/test_ontologies/ontology_types.ttl"
        self.shapes_file = self.base_path / "tests/fixtures/test_ontologies/ontology_types_shapes.ttl"
        
        # Load ontology and shapes graphs
        self.ontology_graph = Graph()
        self.ontology_graph.parse(self.ontology_file, format="turtle")
        
        self.shapes_graph = Graph()
        self.shapes_graph.parse(self.shapes_file, format="turtle")
        
        # Define namespace
        self.ns = Namespace("http://example.org/ontology#")

    def test_validation_rule_types(self):
        """Test that all ValidationRuleType instances are valid"""
        validation_types = [
            "RISK", "MATRIX", "SEMANTIC", "SYNTAX", "SPORE"
        ]
        
        for type_name in validation_types:
            uri = self.ns[type_name]
            self.assertTrue(
                (uri, None, self.ns.ValidationRuleType) in self.ontology_graph,
                f"ValidationRuleType {type_name} not found in ontology"
            )

    def test_error_severity_levels(self):
        """Test that all ErrorSeverity levels are valid"""
        severity_levels = [
            "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"
        ]
        
        for level in severity_levels:
            uri = self.ns[level]
            self.assertTrue(
                (uri, None, self.ns.ErrorSeverity) in self.ontology_graph,
                f"ErrorSeverity {level} not found in ontology"
            )

    def test_compliance_levels(self):
        """Test that all ComplianceLevel values are valid"""
        compliance_levels = [
            "NOT_STARTED", "PARTIAL", "SUBSTANTIAL", "FULL"
        ]
        
        for level in compliance_levels:
            uri = self.ns[level]
            self.assertTrue(
                (uri, None, self.ns.ComplianceLevel) in self.ontology_graph,
                f"ComplianceLevel {level} not found in ontology"
            )

    def test_shacl_validation(self):
        """Test that the ontology validates against SHACL shapes"""
        conforms, results_graph, results_text = validate(
            self.ontology_graph,
            shacl_graph=self.shapes_graph,
            inference='rdfs',
            debug=True
        )
        
        self.assertTrue(
            conforms, 
            f"SHACL validation failed with the following results:\n{results_text}"
        )

    def test_required_properties(self):
        """Test that all classes have required properties (label and comment)"""
        classes = [
            "ValidationRuleType",
            "ErrorSeverity",
            "ComplianceLevel"
        ]
        
        for class_name in classes:
            class_uri = self.ns[class_name]
            # Check label
            self.assertTrue(
                (class_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), None) 
                in self.ontology_graph,
                f"Class {class_name} missing rdfs:label"
            )
            # Check comment
            self.assertTrue(
                (class_uri, URIRef("http://www.w3.org/2000/01/rdf-schema#comment"), None)
                in self.ontology_graph,
                f"Class {class_name} missing rdfs:comment"
            )

if __name__ == '__main__':
    unittest.main() 