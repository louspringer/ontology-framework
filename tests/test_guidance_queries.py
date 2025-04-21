"""Tests for the GuidanceOntology class."""

import unittest
from pathlib import Path
from ontology_framework.modules.guidance import GuidanceOntology

class TestGuidanceQueries(unittest.TestCase):
    """Test cases for querying the guidance ontology."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.guidance = GuidanceOntology()
    
    def test_get_conformance_levels(self) -> None:
        """Test retrieving conformance levels."""
        levels = self.guidance.get_conformance_levels()
        self.assertEqual(len(levels), 3)
        
        # Verify STRICT level
        strict = next(l for l in levels if l["string_representation"] == "STRICT")
        self.assertEqual(strict["label"], "Strict Conformance")
        self.assertEqual(strict["validation_rules"], "All validation rules must pass")
        self.assertEqual(strict["minimum_requirements"], "All required properties must be present")
        self.assertEqual(strict["compliance_metrics"], "100% compliance required")
        
        # Verify all expected levels exist
        level_strings = {l["string_representation"] for l in levels}
        self.assertEqual(level_strings, {"STRICT", "MODERATE", "RELAXED"})
    
    def test_get_integration_steps(self) -> None:
        """Test retrieving integration steps."""
        steps = self.guidance.get_integration_steps()
        self.assertGreater(len(steps), 0)
        
        # Verify first step
        first_step = next(s for s in steps if s["order"] == "1")
        self.assertEqual(first_step["label"], "Step 1")
        self.assertEqual(first_step["description"], "First integration step")
    
    def test_get_test_protocols(self) -> None:
        """Test retrieving test protocols."""
        protocols = self.guidance.get_test_protocols()
        self.assertGreater(len(protocols), 0)
        
        # Verify sample protocol
        sample = next(p for p in protocols if "Sample" in p["label"])
        self.assertEqual(sample["conformance_level"], "STRICT")
        self.assertTrue(sample["requires_namespace_validation"])
        self.assertTrue(sample["requires_prefix_validation"])
    
    def test_get_validation_patterns(self) -> None:
        """Test retrieving validation patterns."""
        patterns = self.guidance.get_validation_patterns()
        self.assertGreater(len(patterns), 0)
        
        # Verify shape validation pattern
        shape_pattern = next(p for p in patterns if "Shape" in p["label"])
        self.assertEqual(shape_pattern["priority"], "HIGH")
        self.assertIn("node shapes", shape_pattern["description"].lower())
    
    def test_get_shacl_shapes(self) -> None:
        """Test retrieving SHACL shapes."""
        shapes = self.guidance.get_shacl_shapes()
        self.assertGreater(len(shapes), 0)
        
        # Verify conformance level shape
        conf_shape = next(s for s in shapes if "Conformance" in s["label"])
        self.assertTrue(any(p["path"].endswith("hasStringRepresentation") for p in conf_shape["properties"]))
        self.assertTrue(any(p["path"].endswith("hasValidationRules") for p in conf_shape["properties"]))
    
    def test_validate_conformance_level(self) -> None:
        """Test conformance level validation."""
        self.assertTrue(self.guidance.validate_conformance_level("STRICT"))
        self.assertTrue(self.guidance.validate_conformance_level("MODERATE"))
        self.assertTrue(self.guidance.validate_conformance_level("RELAXED"))
        self.assertFalse(self.guidance.validate_conformance_level("INVALID"))

if __name__ == "__main__":
    unittest.main() 