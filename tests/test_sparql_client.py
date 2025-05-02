import unittest
from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from ontology_framework.sparql_client import SPARQLClient
import os
import tempfile

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

class TestSPARQLClient(unittest.TestCase):
    def setUp(self):
        self.client = SPARQLClient()
        self.test_ontology = """
        @prefix : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        
        :TestModule a owl:Class ;
            rdfs:label "Test Module"@en ;
            rdfs:comment "A test module for validation"@en .
            
        :TestInstance a :TestModule ;
            rdfs:label "Test Instance"@en ;
            rdfs:comment "A test instance"@en .
        """
        
        # Create temporary file for test ontology
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False)
        self.temp_file.write(self.test_ontology)
        self.temp_file.close()
        
    def tearDown(self):
        os.unlink(self.temp_file.name)
        
    def test_load_ontology(self):
        self.client.load_ontology(self.temp_file.name)
        self.assertTrue(len(self.client.graph) > 0)
        
    def test_query(self):
        self.client.load_ontology(self.temp_file.name)
        query = """
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        SELECT ?module ?label ?comment
        WHERE {
            ?module a owl:Class ;
                    rdfs:label ?label ;
                    rdfs:comment ?comment .
        }
        """
        results = self.client.query(query)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['label'], "Test Module")
        
    def test_update(self):
        self.client.load_ontology(self.temp_file.name)
        update = """
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        INSERT DATA {
            :NewInstance a :TestModule ;
                        rdfs:label "New Instance"@en ;
                        rdfs:comment "A new test instance"@en .
        }
        """
        result = self.client.update(update)
        self.assertEqual(result['status'], "success")
        
        # Verify update
        query = """
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        SELECT ?instance ?label
        WHERE {
            ?instance a :TestModule ;
                     rdfs:label ?label .
        }
        """
        results = self.client.query(query)
        self.assertEqual(len(results), 2)
        
    def test_validate(self):
        self.client.load_ontology(self.temp_file.name)
        result = self.client.validate()
        self.assertTrue(result['conforms'])

if __name__ == '__main__':
    unittest.main() 