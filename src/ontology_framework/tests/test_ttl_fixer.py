"""
Test module for stereo ontology validation.
"""

import unittest
import shutil
import tempfile
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import NoReturn, Dict, List, Tuple, Optional, TypedDict
from pyshacl.consts import SH as SHACL
from pyshacl import validate
from ontology_framework.modules.ttl_fixer import TTLFixer, fix_ttl_file, SHACLShapeBuilder

# Define SHACL namespace using the correct URI
SHACL = SHACL

class FrequencyCase(TypedDict):
    value: str
    expected: bool

class TestTTLFixer(unittest.TestCase):
    """Test cases for TTL file fixing functionality."""
    
    test_dir: Path
    test_ttl: Path
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test environment."""
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.test_ttl = cls.test_dir / "test_stereo.ttl"
        
    def setUp(self) -> None:
        """Set up test data."""
        self.create_test_ttl()
        
    def create_test_ttl(self, content: Optional[str] = None) -> None:
        """Create a test TTL file with known issues."""
        g = Graph()
        
        # Define namespaces
        base_ns = Namespace("./stereo#")
        g.bind("", base_ns)
        g.bind("rdf", RDF)
        g.bind("rdfs", RDFS)
        g.bind("owl", OWL)
        g.bind("xsd", XSD)
        g.bind("sh", SHACL)
        
        # Add class definition
        g.add((base_ns.FrequencySpecification, RDF.type, RDFS.Class))
        g.add((base_ns.FrequencySpecification, RDFS.label, Literal("Frequency Specification")))
        g.add((base_ns.FrequencySpecification, RDFS.comment, Literal("Specifies frequency values for audio equipment")))
        
        # Add property definition
        g.add((base_ns.hasFrequencyValue, RDF.type, RDF.Property))
        g.add((base_ns.hasFrequencyValue, RDFS.domain, base_ns.FrequencySpecification))
        g.add((base_ns.hasFrequencyValue, RDFS.range, XSD.integer))
        g.add((base_ns.hasFrequencyValue, RDFS.label, Literal("has frequency value")))
        g.add((base_ns.hasFrequencyValue, RDFS.comment, Literal("The frequency value in Hz, can be a single value or range (e.g., 50 or '50-75')")))
        
        # Add test instance
        test_freq = base_ns.testFrequency
        g.add((test_freq, RDF.type, base_ns.FrequencySpecification))
        g.add((test_freq, base_ns.hasFrequencyValue, Literal("50-75", datatype=XSD.integer)))
        
        # Serialize to file
        g.serialize(destination=str(self.test_ttl), format="turtle")
        
    def test_invalid_file_path(self) -> None:
        """Test handling of invalid file paths."""
        with self.assertRaises(FileNotFoundError):
            TTLFixer(self.test_dir / "nonexistent.ttl")
            
    def test_invalid_ttl_syntax(self) -> None:
        """Test handling of invalid TTL syntax."""
        invalid_content = """
        @prefix : <./stereo#> .
        :InvalidClass a owl:Class ;
            rdfs:label "Invalid Class" ;
            rdfs:comment "This is invalid TTL syntax
        """
        self.create_test_ttl(invalid_content)
        with self.assertRaises(Exception):
            TTLFixer(self.test_ttl)
        
    def test_fix_prefixes(self) -> None:
        """Test that prefixes are correctly fixed."""
        fixer = TTLFixer(self.test_ttl)
        fixer.fix()
        
        # Load the fixed file and verify prefixes
        g = Graph()
        g.parse(self.test_ttl, format="turtle")
        
        # Check that standard prefixes are present and correct
        self.assertEqual(str(g.namespace_manager.store.namespace("rdf")), str(RDF))
        self.assertEqual(str(g.namespace_manager.store.namespace("rdfs")), str(RDFS))
        self.assertEqual(str(g.namespace_manager.store.namespace("owl")), str(OWL))
        self.assertEqual(str(g.namespace_manager.store.namespace("xsd")), str(XSD))
        self.assertEqual(str(g.namespace_manager.store.namespace("sh")), str(SHACL))
        
    def test_fix_frequency_validation(self) -> None:
        """Test that frequency validation shape is added correctly."""
        # Create test TTL file with known issues
        self.create_test_ttl()
        
        # Fix the file
        fixer = TTLFixer(self.test_ttl)
        fixer.fix()
        
        # Verify the shape exists with correct namespace
        graph = Graph()
        graph.parse(self.test_ttl, format="turtle")
        
        # Get the base URI from the file path
        base_uri = f"file://{self.test_ttl.resolve().parent}/stereo"
        base_ns = Namespace(f"{base_uri}#")
        
        # Verify the shape exists
        shape = URIRef(f"{base_uri}#FrequencySpecificationShape")
        self.assertTrue((shape, RDF.type, SHACL.NodeShape) in graph)
        
        # Verify property constraints
        for s, p, o in graph.triples((shape, SHACL.property, None)):
            prop_constraint = o
            self.assertTrue((prop_constraint, SHACL.path, base_ns.hasFrequencyValue) in graph)
            self.assertTrue((prop_constraint, SHACL.minCount, Literal(1)) in graph)
            self.assertTrue((prop_constraint, SHACL.maxCount, Literal(1)) in graph)
            self.assertTrue((prop_constraint, SHACL.datatype, XSD.integer) in graph)
            self.assertTrue((prop_constraint, SHACL.pattern, Literal("^[1-9][0-9]*(?:-[1-9][0-9]*)?$")) in graph)
        
    def test_frequency_validation_cases(self) -> None:
        """Test frequency validation with various test cases."""
        FREQUENCY_CASES: Dict[str, FrequencyCase] = {
            "valid_single": {"value": "50", "expected": True},
            "valid_range": {"value": "50-75", "expected": True},
            "negative": {"value": "-50", "expected": False},
            "decimal": {"value": "50.5", "expected": False},
            "invalid_chars": {"value": "abc", "expected": False},
            "empty": {"value": "", "expected": False},
            "incomplete_range": {"value": "50-", "expected": False},
            "negative_range": {"value": "-75", "expected": False},
            "multiple_ranges": {"value": "50-75-100", "expected": False}
        }
        
        # Create a shapes graph with just the SHACL shape
        shapes_graph = Graph()
        base_ns = Namespace("./stereo#")
        shapes_graph.bind("", base_ns)
        shapes_graph.bind("sh", SHACL)
        shapes_graph.bind("xsd", XSD)
        
        # Create the shape using SHACLShapeBuilder
        builder = SHACLShapeBuilder(shapes_graph, base_ns)
        shape = builder.create_node_shape(
            "FrequencySpecificationShape",
            base_ns.FrequencySpecification
        )
        
        # Add property constraint
        builder.add_property_constraint(
            shape=shape,
            path=base_ns.hasFrequencyValue,
            min_count=1,
            max_count=1,
            datatype=XSD.integer,
            pattern="^[1-9][0-9]*(?:-[1-9][0-9]*)?$",
            message=(
                "Frequency must be a positive integer (e.g., '50') or a range of "
                "positive integers (e.g., '50-75'). Negative numbers, decimals, "
                "empty values, and malformed ranges are not allowed."
            )
        )
        
        # Add severity level
        shapes_graph.add((shape, SHACL.severity, SHACL.Violation))
        
        for name, case in FREQUENCY_CASES.items():
            with self.subTest(name=name):
                # Create data graph with just the instance data
                data_graph = Graph()
                data_graph.bind("", base_ns)
                
                # Add class and property definitions
                data_graph.add((base_ns.FrequencySpecification, RDF.type, OWL.Class))
                data_graph.add((base_ns.hasFrequencyValue, RDF.type, OWL.DatatypeProperty))
                data_graph.add((base_ns.hasFrequencyValue, RDFS.range, XSD.integer))
                
                # Add test instance
                freq = base_ns[f"freq1"]
                data_graph.add((freq, RDF.type, base_ns.FrequencySpecification))
                data_graph.add((freq, base_ns.hasFrequencyValue, Literal(case["value"], datatype=XSD.integer)))
                
                # Validate with SHACL
                conforms, _, results_text = validate(
                    data_graph=data_graph,
                    shacl_graph=shapes_graph,
                    inference="rdfs",
                    debug=True
                )
                
                self.assertEqual(
                    conforms,
                    case["expected"],
                    f"Validation {'failed' if case['expected'] else 'passed'} "
                    f"unexpectedly for value '{case['value']}'. Results:\n{results_text}"
                )
        
    def test_full_fix(self) -> None:
        """Test that both prefixes and shapes are fixed."""
        fix_ttl_file(self.test_ttl)
        
        # Load the fixed file
        g = Graph()
        g.parse(self.test_ttl, format="turtle")
        
        # Get the absolute URI for the shape
        base_uri = f"file://{self.test_ttl.resolve()}"
        shape = URIRef(base_uri + "#FrequencySpecificationShape")
        
        # Verify both prefixes and shapes are fixed
        self.assertEqual(str(g.namespace_manager.store.namespace("sh")), str(SHACL))
        self.assertTrue((shape, RDF.type, SHACL.NodeShape) in g,
                       "Shape not found in graph or has wrong type")
        
        # Verify property constraints
        found_pattern = False
        for s, p, o in g.triples((None, SHACL.pattern, None)):
            if str(o) == "^[1-9][0-9]*(?:-[1-9][0-9]*)?$":
                found_pattern = True
                break
        self.assertTrue(found_pattern, "Expected frequency validation pattern not found")
        
        # Verify target class
        target_class = URIRef(base_uri + "#FrequencySpecification")
        self.assertTrue((shape, SHACL.targetClass, target_class) in g,
                       "Target class not properly set")
        
        # Verify property path
        property_path = URIRef(base_uri + "#hasFrequencyValue")
        found_path = False
        for s, p, o in g.triples((None, SHACL.path, None)):
            if str(o) == str(property_path):
                found_path = True
                break
        self.assertTrue(found_path, "Expected property path not found")
        
    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up test environment."""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)

if __name__ == '__main__':
    unittest.main() 