"""Test suite for GraphDB model manager."""

import unittest
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from ontology_framework.model.graphdb_model_manager import GraphDBModelManager

# Define namespaces
GDB = Namespace("http://example.org/graphdb#")
REQ = Namespace("http://example.org/requirement#")
RISK = Namespace("http://example.org/risk#")
CONST = Namespace("http://example.org/constraint#")

class TestGraphDBModelManager(unittest.TestCase):
    """Test cases for GraphDBModelManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = GraphDBModelManager()
        self.manager.create_model()
        
    def test_model_creation(self):
        """Test that the model is created correctly."""
        # Check GraphDBClient class
        self.assertTrue((GDB.GraphDBClient, RDF.type, OWL.Class) in self.manager.graph)
        self.assertTrue((GDB.GraphDBClient, RDFS.label, Literal("GraphDB Client")) in self.manager.graph)
        
        # Check properties
        self.assertTrue((GDB.base_url, RDF.type, OWL.DatatypeProperty) in self.manager.graph)
        self.assertTrue((GDB.repository, RDF.type, OWL.DatatypeProperty) in self.manager.graph)
        self.assertTrue((GDB.query, RDF.type, OWL.DatatypeProperty) in self.manager.graph)
        
    def test_requirements(self):
        """Test that requirements are added correctly."""
        self.assertTrue((REQ.SPARQLSupport, RDF.type, REQ.Requirement) in self.manager.graph)
        self.assertTrue((REQ.GraphManagement, RDF.type, REQ.Requirement) in self.manager.graph)
        
    def test_risks(self):
        """Test that risks are added correctly."""
        self.assertTrue((RISK.ConnectionFailure, RDF.type, RISK.Risk) in self.manager.graph)
        self.assertTrue((RISK.DataLoss, RDF.type, RISK.Risk) in self.manager.graph)
        
    def test_constraints(self):
        """Test that constraints are added correctly."""
        self.assertTrue((CONST.GraphDBServer, RDF.type, CONST.Constraint) in self.manager.graph)
        self.assertTrue((CONST.Authentication, RDF.type, CONST.Constraint) in self.manager.graph)
        
    def test_validation(self):
        """Test that the model validates correctly."""
        result = self.manager.validate_model()
        self.assertTrue(result["conforms"])
        
    def test_save_load(self):
        """Test saving and loading the model."""
        # Save in RDF/XML format
        self.manager.save_model(format="xml")
        
        # Create new manager and load
        new_manager = GraphDBModelManager()
        new_manager.load_model(format="xml")
        
        # Check that loaded model matches original
        self.assertEqual(len(self.manager.graph), len(new_manager.graph))
        
    def test_query(self):
        """Test querying the model."""
        # Query for all requirements
        query = """
        SELECT ?req ?label ?comment
        WHERE {
            ?req a req:Requirement .
            ?req rdfs:label ?label .
            ?req rdfs:comment ?comment .
        }
        """
        results = self.manager.query_model(query)
        self.assertIsNotNone(results)
        self.assertTrue(len(list(results)) > 0)
        
if __name__ == "__main__":
    unittest.main() 