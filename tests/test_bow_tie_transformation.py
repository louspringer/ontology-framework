import unittest
import os
from pathlib import Path
from rdflib import Graph, URIRef, Literal, XSD
from rdflib.namespace import RDFS, OWL
from ontology_framework.bow_tie_transformation import BowTieTransformation

class TestBowTieTransformation(unittest.TestCase):
    """Test suite for bow-tie transformation patterns.
    
    This test suite validates the bow-tie transformation pattern ontology
    against the framework's prefix management, validation, and guidance rules.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment and load ontologies."""
        # Create test directory
        cls.test_dir = Path(__file__).parent / 'test_data'
        cls.test_dir.mkdir(exist_ok=True)
        
        # Initialize graphs
        cls.ontology = Graph()
        cls.validation_graph = Graph()
        
        # Load core ontologies
        base_path = Path(__file__).parent.parent
        
        # Load bow-tie ontology
        ontology_path = base_path / 'bow-tie-transformation.ttl'
        if not ontology_path.exists():
            raise FileNotFoundError(f"Ontology file not found at {ontology_path}")
        try:
            cls.ontology.parse(str(ontology_path), format='turtle')
        except Exception as e:
            raise RuntimeError(f"Failed to parse ontology: {str(e)}")
        
        # Load validation ontologies
        validation_paths = [
            base_path / 'guidance.ttl',
            base_path / 'prefix_management.ttl',
            base_path / 'prefix_validation.ttl'
        ]
        
        for path in validation_paths:
            if not path.exists():
                raise FileNotFoundError(f"Validation ontology not found at {path}")
            try:
                cls.validation_graph.parse(str(path), format='turtle')
            except Exception as e:
                raise RuntimeError(f"Failed to parse validation ontology {path}: {str(e)}")
        
        # Define namespaces following prefix management rules
        cls.bt_ns = "./bow-tie-pattern#"  # Relative path for core pattern
        cls.ex_ns = "./bow-tie-examples#"  # Relative path for examples
        
        # Define example instances using proper URIRefs
        cls.jpeg_compression = URIRef(f"{cls.ex_ns}JPEGCompression")
        cls.neural_network_pruning = URIRef(f"{cls.ex_ns}NeuralNetworkPruning")
        cls.text_summarization = URIRef(f"{cls.ex_ns}TextSummarization")
        
        # Define property URIs
        cls.has_lossiness = URIRef(f"{cls.bt_ns}hasLossinessLevel")
    
    def test_prefix_validation(self):
        """Test prefix validation rules."""
        # Check prefix format
        self.assertTrue(self.bt_ns.startswith("./"), "Core prefix must use relative path")
        self.assertTrue(self.ex_ns.startswith("./"), "Example prefix must use relative path")
        
        # Check prefix uniqueness
        prefixes = set()
        for prefix, namespace in self.ontology.namespaces():
            self.assertNotIn(prefix, prefixes, f"Duplicate prefix found: {prefix}")
            prefixes.add(prefix)
    
    def test_jpeg_compression(self):
        """Test JPEG compression transformation."""
        # Create test image
        test_image = self.test_dir / 'test_image.jpg'
        # TODO: Add actual image creation/processing
        
        # Verify transformation
        compression = self.ontology.value(
            subject=self.jpeg_compression,
            predicate=self.has_lossiness
        )
        self.assertIsNotNone(compression, "JPEG compression should have a lossiness level")
        self.assertGreaterEqual(float(compression), 0.0, "Lossiness should be >= 0")
        self.assertLessEqual(float(compression), 1.0, "Lossiness should be <= 1")
    
    def test_neural_network_pruning(self):
        """Test neural network pruning transformation."""
        # Create test network
        test_network = self.test_dir / 'original_network.h5'
        # TODO: Add actual network creation/processing
        
        # Verify transformation
        pruning = self.ontology.value(
            subject=self.neural_network_pruning,
            predicate=self.has_lossiness
        )
        self.assertIsNotNone(pruning, "Neural network pruning should have a lossiness level")
        self.assertGreaterEqual(float(pruning), 0.0, "Lossiness should be >= 0")
        self.assertLessEqual(float(pruning), 1.0, "Lossiness should be <= 1")
    
    def test_text_summarization(self):
        """Test text summarization transformation."""
        # Create test text
        test_text = self.test_dir / 'original_text.txt'
        # TODO: Add actual text creation/processing
        
        # Verify transformation
        summarization = self.ontology.value(
            subject=self.text_summarization,
            predicate=self.has_lossiness
        )
        self.assertIsNotNone(summarization, "Text summarization should have a lossiness level")
        self.assertGreaterEqual(float(summarization), 0.0, "Lossiness should be >= 0")
        self.assertLessEqual(float(summarization), 1.0, "Lossiness should be <= 1")
    
    def test_transformation_chain(self):
        """Test complete transformation chain."""
        # Get all transformation patterns
        patterns = self.ontology.subjects(
            predicate=RDFS.subClassOf,
            object=URIRef(f"{self.bt_ns}TransformationPattern")
        )
        
        for pattern in patterns:
            # Check for required properties
            label = self.ontology.value(
                subject=pattern,
                predicate=RDFS.label
            )
            comment = self.ontology.value(
                subject=pattern,
                predicate=RDFS.comment
            )
            version = self.ontology.value(
                subject=pattern,
                predicate=OWL.versionInfo
            )
            
            self.assertIsNotNone(label, f"Pattern {pattern} should have a label")
            self.assertIsNotNone(comment, f"Pattern {pattern} should have a comment")
            self.assertIsNotNone(version, f"Pattern {pattern} should have a version")
    
    def test_guidance_conformance(self):
        """Test conformance with guidance rules."""
        # Check for required validation rules
        validation_rules = self.validation_graph.subjects(
            predicate=RDFS.subClassOf,
            object=URIRef("http://www.w3.org/ns/shacl#NodeShape")
        )
        
        for rule in validation_rules:
            # Verify each rule is properly defined
            self.assertTrue(
                self.validation_graph.value(
                    subject=rule,
                    predicate=URIRef("http://www.w3.org/ns/shacl#targetClass")
                ),
                f"Validation rule {rule} must have a target class"
            )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Remove test files
        for file in cls.test_dir.glob('*'):
            file.unlink()
        cls.test_dir.rmdir()

    def test_guidance_conformance(self):
        transformation = BowTieTransformation()
        assert transformation.is_guidance_conformant()

    def test_jpeg_compression(self):
        transformation = BowTieTransformation()
        compression = transformation.apply_jpeg_compression("test.jpg", quality=85)
        assert compression is not None
        assert compression.lossiness_level == 0.15  # 85% quality = 15% loss

    def test_neural_network_pruning(self):
        transformation = BowTieTransformation()
        pruning = transformation.apply_neural_network_pruning("model.h5", ratio=0.3)
        assert pruning is not None
        assert pruning.lossiness_level == 0.3  # 30% pruning = 30% loss

    def test_text_summarization(self):
        transformation = BowTieTransformation()
        text = "This is a long text that needs to be summarized for testing purposes."
        summarization = transformation.apply_text_summarization(text, ratio=0.5)
        assert summarization is not None
        assert summarization.lossiness_level == 0.5  # 50% summarization = 50% loss

    def test_prefix_validation(self):
        transformation = BowTieTransformation()
        assert transformation.validate_prefixes()

    def test_transformation_chain(self):
        transformation = BowTieTransformation()
        result = transformation.apply_transformation_chain("input.txt")
        assert result is not None
        assert result.is_valid  # Access is_valid as a property

if __name__ == '__main__':
    unittest.main() 