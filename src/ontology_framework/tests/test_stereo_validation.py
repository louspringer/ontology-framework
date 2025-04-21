"""
Test module for stereo ontology validation.
"""

import unittest
import shutil
from pathlib import Path
from typing import ClassVar, Dict, TypedDict, Union
from rdflib import Graph, URIRef, Literal, RDF
from pyshacl import validate
from pyshacl.consts import SH
from ontology_framework.modules.ttl_fixer import fix_ttl_file

class FrequencyCase(TypedDict):
    value: str
    expected: bool

class TestStereoValidation(unittest.TestCase):
    """Test suite for validating stereo ontology and frequency specifications.
    
    This test suite verifies:
    1. Frequency value validation (format and range)
    2. SHACL shape definitions and application
    3. Complete TTL file fixing process
    """
    
    test_data_dir: ClassVar[Path] = Path(__file__).parent / "test_data"
    test_ttl: ClassVar[Path] = test_data_dir / "test_stereo.ttl"
    fixed_ttl: ClassVar[Path] = test_data_dir / "fixed_stereo.ttl"
    
    FREQUENCY_CASES: Dict[str, FrequencyCase] = {
        "valid_single": {"value": "50", "expected": True},
        "valid_range": {"value": "50-75", "expected": True},
        "invalid_empty": {"value": "", "expected": False},
        "invalid_negative": {"value": "-50", "expected": False},
        "invalid_decimal": {"value": "50.5", "expected": False},
        "invalid_format": {"value": "50~75", "expected": False}
    }
    
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test data directory and files."""
        if cls.test_data_dir.exists():
            shutil.rmtree(cls.test_data_dir)
        cls.test_data_dir.mkdir(parents=True)
    
    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up test data directory."""
        if cls.test_data_dir.exists():
            shutil.rmtree(cls.test_data_dir)
    
    def setUp(self) -> None:
        self.create_test_ttl("50-75")  # Default test case
    
    def create_test_ttl(self, frequency_value: str) -> None:
        """Create a test TTL file with the given frequency value.
        
        Args:
            frequency_value: The frequency value to use in the test file.
        """
        # Ensure test directory exists
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test TTL file with the given frequency value
        with open(self.test_ttl, "w") as f:
            f.write(f"""@prefix : <./stereo#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:FrequencySpecification a owl:Class ;
    rdfs:label "Frequency Specification" ;
    rdfs:comment "Specifies a frequency value or range for audio equipment." .

:hasFrequencyValue a owl:DatatypeProperty ;
    rdfs:domain :FrequencySpecification ;
    rdfs:range xsd:string ;
    rdfs:label "has frequency value" ;
    rdfs:comment "The frequency value in Hz, can be a single value or range (e.g., '50' or '50-75')." .

:FrequencySpecificationShape a sh:NodeShape ;
    sh:targetClass :FrequencySpecification ;
    sh:property [
        sh:path :hasFrequencyValue ;
        sh:datatype xsd:string ;
        sh:pattern "^[0-9]+(-[0-9]+)?$" ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Frequency value must be a positive integer or range (e.g., '50' or '50-75')" ;
    ] .

:testFrequency a :FrequencySpecification ;
    :hasFrequencyValue "{frequency_value}" .""")
    
    def test_frequency_datatype(self) -> None:
        """Test that frequency values are properly validated."""
        for case_name, case_data in self.FREQUENCY_CASES.items():
            with self.subTest(case=case_name):
                self.create_test_ttl(case_data["value"])  # Pass only the string value
                g = Graph()
                g.parse(self.test_ttl, format="turtle")
                conforms, _, _ = validate(g)
                self.assertEqual(conforms, case_data["expected"], 
                    f"Frequency validation failed for {case_name} with value {case_data['value']}")
    
    def test_shacl_shapes(self) -> None:
        """Test that SHACL shapes are properly defined and validated."""
        g = Graph()
        g.parse(self.test_ttl, format="turtle")
        shape_uri = URIRef("file://" + str(self.test_ttl.resolve().parent) + "/stereo#FrequencySpecificationShape")
        self.assertIn((shape_uri, RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape")), g,
            "FrequencySpecificationShape not found in graph")
    
    def test_fix_stereo_ttl(self) -> None:
        """Test that the TTL fixer correctly handles frequency validation."""
        # Create a copy of test file to fix
        shutil.copy2(self.test_ttl, self.fixed_ttl)
        fix_ttl_file(str(self.fixed_ttl))  # Fix takes a string path
        g = Graph()
        g.parse(self.fixed_ttl, format="turtle")
        conforms, _, _ = validate(g)
        self.assertTrue(conforms, "Fixed TTL file should pass SHACL validation")

if __name__ == '__main__':
    unittest.main() 