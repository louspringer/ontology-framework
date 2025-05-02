"""Test suite for guidance manager."""

import unittest
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD
from ontology_framework.tools.guidance_manager import GuidanceManager
from pathlib import Path
import tempfile
import shutil

class TestGuidanceManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment with semantic web tools."""
        self.test_dir = tempfile.mkdtemp()
        self.test_guidance = Path(self.test_dir) / 'test_guidance.ttl'
        
        # Create test guidance ontology using SPARQL
        self.test_graph = Graph()
        GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
        self.test_graph.bind('guidance', GUIDANCE)
        self.test_graph.bind('rdfs', RDFS)
        self.test_graph.bind('owl', OWL)
        self.test_graph.bind('xsd', XSD)
        
        # Add test data using SPARQL Update
        update_query = """
        PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        INSERT DATA {
            guidance:TestPattern 
                a guidance:ValidationPattern ;
                rdfs:label "Test Pattern" ;
                rdfs:comment "A test validation pattern" ;
                guidance:hasType "TEST" .
                
            guidance:TestRule
                a guidance:ValidationRule ;
                rdfs:label "Test Rule" ;
                rdfs:comment "A test validation rule" ;
                guidance:hasType "TEST" ;
                guidance:hasMessage "Test validation failed" ;
                guidance:hasPriority "1"^^xsd:integer .
        }
        """
        self.test_graph.update(update_query)
        
        # Save and initialize manager
        self.test_graph.serialize(destination=str(self.test_guidance), format='turtle')
        self.manager = GuidanceManager(str(self.test_guidance))
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def test_get_validation_patterns(self):
        """Test retrieving validation patterns using SPARQL."""
        patterns = self.manager.get_validation_patterns()
        self.assertEqual(len(patterns), 1)
        pattern = patterns[0]
        self.assertEqual(pattern['label'], "Test Pattern")
        self.assertEqual(pattern['type'], "TEST")
        
    def test_get_validation_rules(self):
        """Test retrieving validation rules using SPARQL."""
        rules = self.manager.get_validation_rules()
        self.assertEqual(len(rules), 1)
        rule = rules[0]
        self.assertEqual(rule['message'], "Test validation failed")
        self.assertEqual(rule['priority'], "1")
        
    def test_validate_guidance(self):
        """Test guidance ontology validation using SHACL."""
        # Add SHACL shapes using SPARQL Update
        update_query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        INSERT DATA {
            guidance:ValidationRuleShape 
                a sh:NodeShape ;
                sh:targetClass guidance:ValidationRule ;
                sh:property [
                    sh:path guidance:hasMessage ;
                    sh:datatype xsd:string ;
                    sh:minCount 1 ;
                    sh:maxCount 1
                ] ;
                sh:property [
                    sh:path guidance:hasType ;
                    sh:datatype xsd:string ;
                    sh:minCount 1 ;
                    sh:maxCount 1
                ] ;
                sh:property [
                    sh:path guidance:hasPriority ;
                    sh:datatype xsd:integer ;
                    sh:minCount 1 ;
                    sh:maxCount 1
                ] ;
                sh:property [
                    sh:path rdfs:label ;
                    sh:datatype xsd:string ;
                    sh:minCount 1 ;
                    sh:maxCount 1
                ] .
                
            guidance:ValidationPatternShape
                a sh:NodeShape ;
                sh:targetClass guidance:ValidationPattern ;
                sh:property [
                    sh:path guidance:hasType ;
                    sh:datatype xsd:string ;
                    sh:minCount 1 ;
                    sh:maxCount 1
                ] ;
                sh:property [
                    sh:path rdfs:label ;
                    sh:datatype xsd:string ;
                    sh:minCount 1 ;
                    sh:maxCount 1
                ] ;
                sh:property [
                    sh:path rdfs:comment ;
                    sh:datatype xsd:string ;
                    sh:minCount 1 ;
                    sh:maxCount 1
                ] .
        }
        """
        self.manager.graph.update(update_query)
        
        results = self.manager.validate_guidance()
        self.assertEqual(len(results['errors']), 0, f"Validation errors found: {results['errors']}")
        self.assertEqual(len(results['warnings']), 0, f"Validation warnings found: {results['warnings']}")
        
        # Test invalid data
        invalid_query = """
        PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
        
        INSERT DATA {
            guidance:InvalidRule
                a guidance:ValidationRule .
        }
        """
        self.manager.graph.update(invalid_query)
        
        results = self.manager.validate_guidance()
        self.assertGreater(len(results['errors']), 0, "No validation errors found for invalid data")
        
    def test_add_validation_rule(self):
        """Test adding a validation rule."""
        rule_id = "test_rule"
        rule = {"query": "SELECT ?s WHERE { ?s a owl:Class }"}
        rule_type = "SPARQL"
        message = "Test message"
        priority = 2

        rule_uri = self.manager.add_validation_rule(
            rule_id=rule_id,
            rule=rule,
            type=rule_type,
            message=message,
            priority=priority
        )

        # Verify rule was added
        query = """
        SELECT ?type ?message ?priority ?rule_text
        WHERE {
            ?rule a guidance:ValidationRule ;
                guidance:hasSPARQLQuery ?rule_text ;
                guidance:hasType ?type ;
                guidance:hasMessage ?message ;
                guidance:hasPriority ?priority .
        }
        """
        results = list(self.manager.graph.query(query))
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(str(result.type), rule_type)
        self.assertEqual(str(result.message), message)
        self.assertEqual(int(result.priority), priority)
        self.assertEqual(str(result.rule_text), rule["query"])
        
    def test_save_and_reload(self):
        """Test saving and reloading the guidance ontology."""
        # Add a test rule
        rule_id = "test_rule"
        rule = {"query": "SELECT ?s WHERE { ?s a owl:Class }"}
        rule_type = "SPARQL"
        message = "Test message"
        priority = 2

        self.manager.add_validation_rule(
            rule_id=rule_id,
            rule=rule,
            type=rule_type,
            message=message,
            priority=priority
        )

        # Save to temp file
        save_path = Path(self.test_dir) / "test_guidance.ttl"
        self.manager.save(str(save_path))

        # Create new manager and load saved file
        new_manager = GuidanceManager()
        new_manager.load(str(save_path))

        # Verify rule exists in new manager
        query = """
        SELECT ?type ?message ?priority ?rule_text
        WHERE {
            ?rule a guidance:ValidationRule ;
                guidance:hasSPARQLQuery ?rule_text ;
                guidance:hasType ?type ;
                guidance:hasMessage ?message ;
                guidance:hasPriority ?priority .
        }
        """
        results = list(new_manager.graph.query(query))
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(str(result.type), rule_type)
        self.assertEqual(str(result.message), message)
        self.assertEqual(int(result.priority), priority)
        self.assertEqual(str(result.rule_text), rule["query"])

if __name__ == '__main__':
    unittest.main() 