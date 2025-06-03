import unittest
from rdflib import Graph, URIRef, Namespace
from spore_validation import SporeValidator

class TestSporeValidator(unittest.TestCase):
    def setUp(self):
        self.validator = SporeValidator()
        self.test_spore = URIRef("http://example.org/spores/test-spore")
        
    def test_pattern_registration(self):
        """Test pattern registration validation"""
        # Add test data to graph
        self.validator.graph.add((self.test_spore RDF.type, META.TransformationPattern))
        
        results = self.validator.validate_spore(self.test_spore)
        self.assertTrue(results["pattern_registration"])
        
    def test_shacl_validation(self):
        """Test SHACL validation rules"""
        # Add test data to graph
        self.validator.graph.add((self.test_spore RDF.type, META.TransformationPattern))
        shape = URIRef("http://example.org/shapes/test-shape")
        self.validator.graph.add((shape, RDF.type, SH.NodeShape))
        self.validator.graph.add((shape, SH.targetClass, self.test_spore))
        
        results = self.validator.validate_spore(self.test_spore)
        self.assertTrue(results["shacl_validation"])
        
    def test_patch_support(self):
        """Test patch distribution support"""
        # Add test data to graph
        patch = URIRef("http://example.org/patches/test-patch")
        self.validator.graph.add((self.test_spore META.distributesPatch, patch))
        self.validator.graph.add((patch, RDF.type, META.ConceptPatch))
        
        results = self.validator.validate_spore(self.test_spore)
        self.assertTrue(results["patch_support"])
        
    def test_conformance_tracking(self):
        """Test conformance violation tracking"""
        # Add test data to graph
        violation = URIRef("http://example.org/violations/test-violation")
        self.validator.graph.add((self.test_spore META.confirmedViolation, violation))
        
        results = self.validator.validate_spore(self.test_spore)
        self.assertTrue(results["conformance_tracking"])

if __name__ == "__main__":
    unittest.main() 