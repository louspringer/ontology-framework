import unittest
import os
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS
from register_ontology import update_session_ttl

class TestSessionUpdate(unittest.TestCase):
    def setUp(self):
        self.test_session_file = Path('test_session.ttl')
        if self.test_session_file.exists():
            self.test_session_file.unlink()
            
    def tearDown(self):
        if self.test_session_file.exists():
            self.test_session_file.unlink()
            
    def test_session_update_rdflib_terms(self):
        """Test that session updates properly handle RDFLib terms"""
        # Test data
        ontology_info = {
            'uri': 'http://test.com/ontology#',
            'label': 'test',
            'version': '1.0.0'
        }
        model_name = 'TEST_MODEL'
        
        # Update session
        update_session_ttl(ontology_info, model_name, session_file=self.test_session_file)
        
        # Debug: Print file contents
        print("\nSession file contents:")
        with open(self.test_session_file) as f:
            print(f.read())
        
        # Verify session contents
        g = Graph()
        g.parse(self.test_session_file, format='turtle')
        
        # Use absolute URI for session namespace
        base_uri = f"file://{os.path.abspath(os.path.dirname(self.test_session_file))}"
        SESSION = Namespace(f"{base_uri}/session#")
        registration_node = URIRef(f"{SESSION}{model_name}")
        
        # Debug: Print all triples
        print("\nAll triples in graph:")
        for s, p, o in g:
            print(f"{s} {p} {o}")
        
        # Check that all required triples exist with proper RDFLib terms
        self.assertTrue(
            (registration_node, SESSION.hasModelName, Literal(model_name)) in g,
            "Model name should be stored as Literal"
        )
        self.assertTrue(
            (registration_node, SESSION.hasVersion, Literal(ontology_info['version'])) in g,
            "Version should be stored as Literal"
        )
        self.assertTrue(
            (registration_node, RDFS.label, Literal(ontology_info['label'])) in g,
            "Label should be stored as Literal"
        )

if __name__ == '__main__':
    unittest.main() 