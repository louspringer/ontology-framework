import unittest
from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from scripts.update_module_constraints import update_module_constraints
from ontology_framework.sparql_client import SPARQLClient
import os
import tempfile

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
SH = Namespace("http://www.w3.org/ns/shacl#")

class TestModuleConstraints(unittest.TestCase):
    def setUp(self):
        # Create test ontology
        self.test_ontology = """
        @prefix : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        
        :CoreModule a owl:Class ;
            rdfs:label "Core Module"@en ;
            rdfs:comment "Essential framework modules"@en .
            
        :IntegrationPattern a owl:Class ;
            rdfs:label "Integration Pattern"@en ;
            rdfs:comment "Patterns for module integration"@en .
        """
        
        # Create temporary file for test ontology
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False)
        self.temp_file.write(self.test_ontology)
        self.temp_file.close()
        
        # Set environment variable for test ontology path
        os.environ['GUIDANCE_ONTOLOGY_PATH'] = self.temp_file.name
        
    def tearDown(self):
        os.unlink(self.temp_file.name)
        if 'GUIDANCE_ONTOLOGY_PATH' in os.environ:
            del os.environ['GUIDANCE_ONTOLOGY_PATH']
            
    def test_update_module_constraints(self):
        # Run the update
        success = update_module_constraints(self.temp_file.name)
        self.assertTrue(success)
        
        # Save the updated graph back to the temp file
        client = SPARQLClient()
        client.load_ontology(self.temp_file.name)
        client.graph.serialize(destination=self.temp_file.name, format="turtle")
        
        # Verify the constraints were added
        client = SPARQLClient()
        client.load_ontology(self.temp_file.name)
        
        # Check ModuleShape
        query = """
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        
        ASK {
            :ModuleShape a sh:NodeShape ;
                        sh:targetClass :CoreModule ;
                        sh:property ?label_property ;
                        sh:property ?comment_property ;
                        sh:property ?integration_property .
            
            ?label_property sh:path rdfs:label ;
                           sh:minCount 1 ;
                           sh:maxCount 1 ;
                           sh:datatype rdfs:Literal ;
                           sh:languageIn "en" .
        }
        """
        result = client.query(query)
        self.assertTrue(result[0]['ASK'])
        
        # Check IntegrationPatternShape
        query = """
        PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        
        ASK {
            :IntegrationPatternShape a sh:NodeShape ;
                                    sh:targetClass :IntegrationPattern ;
                                    sh:property ?label_property ;
                                    sh:property ?source_property ;
                                    sh:property ?target_property .
            
            ?label_property sh:path rdfs:label ;
                           sh:minCount 1 ;
                           sh:maxCount 1 ;
                           sh:datatype rdfs:Literal .
        }
        """
        result = client.query(query)
        self.assertTrue(result[0]['ASK'])

if __name__ == '__main__':
    unittest.main() 