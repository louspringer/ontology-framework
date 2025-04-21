"""
Test module for BowTieTransformation class.
"""

import os
import shutil
import unittest
from typing import ClassVar
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
from ontology_framework.bow_tie_transformation import BowTieTransformation
from ontology_framework.conformance_tracking import ConformanceTracker

class TestBowTieTransformation(unittest.TestCase):
    """Test cases for BowTieTransformation class."""
    
    test_dir: ClassVar[str]
    test_ontology_path: ClassVar[str]
    ontology: ClassVar[Graph]
    tracker: ClassVar[ConformanceTracker]
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test environment."""
        # Create test directories
        cls.test_dir = "tests/test_data"
        os.makedirs(cls.test_dir, exist_ok=True)
        
        # Create a test ontology file
        cls.test_ontology_path = os.path.join(cls.test_dir, "test_ontology.ttl")
        cls.ontology = Graph()
        
        # Add some test data
        test_ns = Namespace("http://example.org/test#")
        cls.ontology.bind("test", test_ns)
        cls.ontology.add((test_ns.TestTransformation, RDF.type, OWL.Class))
        cls.ontology.add((test_ns.TestInput, RDF.type, OWL.Class))
        cls.ontology.add((test_ns.TestOutput, RDF.type, OWL.Class))
        
        # Save the test ontology
        cls.ontology.serialize(destination=cls.test_ontology_path, format="turtle")
        
        # Initialize conformance tracker
        cls.tracker = ConformanceTracker(guidance_graph=cls.ontology)
        
    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up test environment."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        
    def test_guidance_conformance(self) -> None:
        """Test that the transformation follows guidance rules."""
        # Create transformation chain
        transformer = BowTieTransformation(self.ontology)
        
        # Transform the graph and validate it
        transformed_graph = transformer.transform()
        self.assertIsNotNone(transformed_graph, "Transformation should return a graph")
        
        # Create a new transformer with the transformed graph
        validator = BowTieTransformation(transformed_graph)
        
        # Validate the transformed graph
        is_valid = validator.validate()
        self.assertTrue(is_valid, "Transformation should follow bow-tie pattern")
        
    def test_transformation_chain(self) -> None:
        """Test the transformation chain."""
        # Create transformation chain
        transformer = BowTieTransformation(self.ontology)
        
        # Transform the graph
        transformed_graph = transformer.transform()
        self.assertIsNotNone(transformed_graph, "Transformation should return a graph")
        
        # Check if required classes exist
        bt_ns = Namespace("https://github.com/louspringer/ontology-framework/bow-tie#")
        required_classes = {
            bt_ns.Transformation,
            bt_ns.Input,
            bt_ns.Output
        }
        
        for cls in required_classes:
            self.assertTrue(
                (cls, RDF.type, OWL.Class) in transformed_graph,
                f"Required class {cls} not found in transformed graph"
            )
            
    def test_validation_patterns(self) -> None:
        """Test validation patterns."""
        # Create transformation chain
        transformer = BowTieTransformation(self.ontology)
        
        # Transform the graph
        transformed_graph = transformer.transform()
        self.assertIsNotNone(transformed_graph, "Transformation should return a graph")
        
        # Create a new transformer with the transformed graph
        validator = BowTieTransformation(transformed_graph)
        
        # Check SHACL validation rules
        query = """
        PREFIX bt: <https://github.com/louspringer/ontology-framework/bow-tie#>
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        ASK {
            ?shape a sh:NodeShape .
            ?shape sh:targetClass bt:Transformation .
            ?shape sh:property ?input_property .
            ?input_property sh:path bt:hasInput .
            ?input_property sh:minCount 1 .
            ?input_property sh:maxCount 1 .
            ?shape sh:property ?output_property .
            ?output_property sh:path bt:hasOutput .
            ?output_property sh:minCount 1 .
            ?output_property sh:maxCount 1 .
        }
        """
        self.assertTrue(
            bool(transformed_graph.query(query).askAnswer),
            "SHACL validation rules not properly applied"
        )

if __name__ == "__main__":
    unittest.main()