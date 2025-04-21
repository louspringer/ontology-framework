"""Test suite for guidance ontology consistency."""

import unittest
from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF, RDFS, OWL, XSD, SH
from rdflib.namespace import RDF, RDFS, OWL, XSD
from src.ontology_framework.modules.guidance import GuidanceOntology

class TestGuidanceConsistency(unittest.TestCase):
    """Test suite for guidance ontology consistency."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.guidance_file = Path("guidance.ttl")
        self.python_guidance = GuidanceOntology()
        self.python_guidance.emit(self.guidance_file)
        
    def test_emit_reload_consistency(self) -> None:
        """Test that emitting and reloading produces the same graph."""
        # Load the emitted file
        loaded_guidance = GuidanceOntology(str(self.guidance_file))
        
        # Compare the graphs semantically
        self.assertTrue(
            self._compare_graphs_semantically(self.python_guidance.graph, loaded_guidance.graph),
            "Emitted and reloaded graphs are not semantically equivalent"
        )
        
    def test_guidance_structure(self) -> None:
        """Test that the guidance ontology has the expected structure."""
        # Check for required classes
        required_classes = {
            "ConformanceLevel",
            "IntegrationProcess",
            "IntegrationStep",
            "ModelConformance",
            "TestProtocol",
            "TestPhase",
            "TestCoverage",
            "TODO",
            "SHACLValidation",
            "ValidationPattern",
            "IntegrationRequirement"
        }
        
        for class_name in required_classes:
            class_uri = self.python_guidance.base[class_name]
            self.assertTrue(
                (class_uri, RDF.type, OWL.Class) in self.python_guidance.graph,
                f"Required class {class_name} not found in ontology"
            )
            
    def test_round_trip_consistency(self) -> None:
        """Test that Python-generated ontology is semantically equivalent to the Turtle file."""
        # Load the original Turtle file
        original_graph = Graph()
        original_graph.parse(self.guidance_file, format="turtle")
        
        # Compare the graphs semantically
        self.assertTrue(
            self._compare_graphs_semantically(self.python_guidance.graph, original_graph),
            "Python-generated and Turtle ontologies are not semantically equivalent"
        )
        
    def test_shacl_validation_patterns(self):
        """Test that SHACL validation patterns are correctly defined."""
        # Test ConformanceLevelShape
        conformance_shape = self.python_guidance.ConformanceLevelShape
        self.assertTrue(any(self.python_guidance.graph.triples((conformance_shape, RDF.type, SH.NodeShape))))
        self.assertTrue(any(self.python_guidance.graph.triples((conformance_shape, SH.targetClass, self.python_guidance.ConformanceLevel))))
        
        # Test required properties for ConformanceLevel
        required_props = [
            self.python_guidance.hasStringRepresentation,
            self.python_guidance.hasValidationRules,
            self.python_guidance.hasMinimumRequirements,
            self.python_guidance.hasComplianceMetrics
        ]
        for prop in required_props:
            self.assertTrue(any(self.python_guidance.graph.triples((conformance_shape, SH.property, None))))
            
        # Test IntegrationProcessShape
        process_shape = self.python_guidance.IntegrationProcessShape
        self.assertTrue(any(self.python_guidance.graph.triples((process_shape, RDF.type, SH.NodeShape))))
        self.assertTrue(any(self.python_guidance.graph.triples((process_shape, SH.targetClass, self.python_guidance.IntegrationProcess))))
        
        # Test cardinality constraints
        step_property = next(self.python_guidance.graph.triples((process_shape, SH.property, None)))[2]
        self.assertTrue(any(self.python_guidance.graph.triples((step_property, SH.minCount, Literal(1)))))
        
    def _compare_graphs_semantically(self, graph1: Graph, graph2: Graph) -> bool:
        """Compare two graphs semantically, ignoring order of triples."""
        # Compare number of triples
        if len(graph1) != len(graph2):
            return False
            
        # Compare subjects
        subjects1 = set(graph1.subjects())
        subjects2 = set(graph2.subjects())
        if subjects1 != subjects2:
            return False
            
        # Compare predicates
        predicates1 = set(graph1.predicates())
        predicates2 = set(graph2.predicates())
        if predicates1 != predicates2:
            return False
            
        # Compare objects
        objects1 = set(graph1.objects())
        objects2 = set(graph2.objects())
        if objects1 != objects2:
            return False
            
        # Compare all triples
        triples1 = set(graph1)
        triples2 = set(graph2)
        return triples1 == triples2

if __name__ == "__main__":
    unittest.main()