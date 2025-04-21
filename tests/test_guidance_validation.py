"""Tests for validating the guidance ontology."""

import unittest
from pathlib import Path
from rdflib import Graph
from ontology_framework.ontology_validator import OntologyValidator

class TestGuidanceValidation(unittest.TestCase):
    """Test cases for validating the guidance ontology."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.guidance_graph = Graph()
        project_root = Path(__file__).parent.parent
        guidance_path = project_root / "guidance.ttl"
        self.guidance_graph.parse(str(guidance_path), format="turtle")
        self.validator = OntologyValidator(self.guidance_graph)
    
    def test_validate_conformance_levels(self) -> None:
        """Test validation of conformance levels."""
        results = self.validator.validate_conformance_levels()
        self.assertEqual(len(results["errors"]), 0, 
                        f"Found validation errors: {results['errors']}")
    
    def test_validate_integration_process(self) -> None:
        """Test validation of integration process."""
        results = self.validator.validate_integration_process()
        self.assertEqual(len(results["errors"]), 0,
                        f"Found validation errors: {results['errors']}")
    
    def test_validate_test_protocol(self) -> None:
        """Test validation of test protocol."""
        results = self.validator.validate_test_protocol()
        self.assertEqual(len(results["errors"]), 0,
                        f"Found validation errors: {results['errors']}")
    
    def test_validate_guidance_ontology(self) -> None:
        """Test validation of entire guidance ontology."""
        results = self.validator.validate_guidance_ontology()
        self.assertEqual(len(results["errors"]), 0,
                        f"Found validation errors: {results['errors']}")

if __name__ == "__main__":
    unittest.main() 