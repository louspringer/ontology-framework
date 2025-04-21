"""
Test module for TTL file fixing functionality.
"""

import unittest
import shutil
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import NoReturn
from pyshacl.consts import SH

from ontology_framework.modules.ttl_fixer import TTLFixer, fix_ttl_file

# Define SHACL namespace using the correct URI
SHACL = SH

class TestTTLFixer(unittest.TestCase):
    """Test cases for TTL file fixing functionality."""
    
    def setUp(self) -> None:
        """Set up test data."""
        self.test_dir = Path(__file__).parent / "test_data"
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(exist_ok=True)
        
        self.test_ttl = self.test_dir / "test.ttl"
        self.create_test_ttl()
        self.ttl_fixer = TTLFixer(self.test_ttl)
        
    def create_test_ttl(self) -> None:
        """Create a test TTL file with known issues."""
        content = """
        @prefix ex: <./test#> .
        @prefix rdfs: <http:/www.w3.org/2000/01/rdf-schema#> .
        @prefix owl: <http:/www.w3.org/2002/07/owl#> .
        @prefix xsd: <http:/www.w3.org/2001/XMLSchema#> .

        ex:TestClass a owl:Class ;
            rdfs:label "Test Class" ;
            rdfs:comment "A test class for validation" .

        ex:FrequencySpecification a owl:Class ;
            rdfs:label "Frequency Specification" ;
            rdfs:comment "Specifies a frequency value in Hz" .

        ex:hasFrequencyValue a owl:DatatypeProperty ;
            rdfs:domain ex:FrequencySpecification ;
            rdfs:range xsd:string .

        ex:testFreq a ex:FrequencySpecification ;
            ex:hasFrequencyValue "50-75" .
        """
        self.test_ttl.write_text(content)
        
    def test_fix_prefixes_and_uris(self) -> None:
        """Test that prefixes and URIs are fixed correctly."""
        self.ttl_fixer.fix()
        
        # Load the fixed file and verify prefixes and URIs
        g = Graph()
        g.parse(self.test_ttl, format="turtle")
        
        # Check that standard prefixes are present and correct
        self.assertEqual(str(g.namespace_manager.store.namespace("rdf")), str(RDF))
        self.assertEqual(str(g.namespace_manager.store.namespace("rdfs")), str(RDFS))
        self.assertEqual(str(g.namespace_manager.store.namespace("owl")), str(OWL))
        self.assertEqual(str(g.namespace_manager.store.namespace("xsd")), str(XSD))
        self.assertEqual(str(g.namespace_manager.store.namespace("sh")), str(SHACL))
        
        # Check that URIs are properly formatted
        for s, p, o in g:
            if isinstance(s, URIRef):
                self.assertTrue(str(s).startswith("file://") or str(s).startswith("http://"))
            if isinstance(o, URIRef):
                self.assertTrue(str(o).startswith("file://") or str(o).startswith("http://"))
                
    def test_frequency_validation(self) -> None:
        """Test that frequency validation SHACL shape is added correctly."""
        self.ttl_fixer.fix()
        
        # Load the fixed file and verify SHACL shape
        g = Graph()
        g.parse(self.test_ttl, format="turtle")
        
        # Get the base URI for the file
        base_uri = f"file://{self.test_ttl.resolve()}"
        shape_uri = URIRef(f"{base_uri}#FrequencySpecificationShape")
        
        # Check that the shape exists
        self.assertTrue((shape_uri, RDF.type, SHACL.NodeShape) in g)
        
        # Check that the shape has the correct properties
        value_constraint = None
        for s, p, o in g.triples((shape_uri, SHACL.property, None)):
            value_constraint = o
            break
            
        self.assertIsNotNone(value_constraint)
        self.assertTrue(isinstance(value_constraint, BNode))
        
        # Check constraint properties
        self.assertTrue((value_constraint, SHACL.datatype, XSD.string) in g)
        self.assertTrue((value_constraint, SHACL.pattern, Literal("^[0-9]+(-[0-9]+)?$")) in g)
        self.assertTrue((value_constraint, SHACL.minCount, Literal(1)) in g)
        self.assertTrue((value_constraint, SHACL.maxCount, Literal(1)) in g)
                
    def tearDown(self) -> None:
        """Clean up test data."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main() 