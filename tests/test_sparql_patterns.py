"""
Tests for SPARQL patterns in the ontology framework.

This module tests SPARQL pattern recognition, validation, and application
with semantic compliance and ontology framework integration.
"""

# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: 1.0.0
# Behavioral-Profile: ClaudeReflector

import unittest
import logging
import datetime
import os
from rdflib import (
    Graph,
    Namespace,
    RDF,
    RDFS,
    OWL,
    XSD
)
from rdflib.namespace import SH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSPARQLPatterns(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        logger.info("Setting up test environment")
        self.graph = Graph()
        
        # Get absolute paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        guidance_path = os.path.join(base_dir, "guidance.ttl")
        testing_path = os.path.join(base_dir, "guidance/modules/testing.ttl")
        error_path = os.path.join(base_dir, "guidance/modules/runtime_error_handling.ttl")
        
        logger.info(f"Loading ontologies from: {base_dir}")
        
        # Load ontologies
        self.graph.parse(guidance_path, format="turtle")
        self.graph.parse(testing_path, format="turtle")
        self.graph.parse(error_path, format="turtle")
        
        # Define namespaces
        self.test = Namespace("file:///Users/lou/Documents/ontology-framework/guidance/modules/testing#")
        self.error = Namespace("file:///Users/lou/Documents/ontology-framework/guidance/modules/runtime_error_handling#")
        self.guidance = Namespace("file:///Users/lou/Documents/ontology-framework/guidance#")
        
        # Bind namespaces
        self.graph.bind("test", self.test)
        self.graph.bind("error", self.error)
        self.graph.bind("guidance", self.guidance)
        
        logger.info("Test environment setup complete")
        
        # Debug: Print all classes in the graph
        logger.info("Classes in graph:")
        for s in self.graph.subjects(RDF.type, OWL.Class):
            logger.info(f"Found class: {s}")

    def test_pattern_recognition(self):
        """Test that SPARQL test patterns are properly recognized"""
        logger.info("Testing SPARQL test pattern recognition")
        
        # Query for test patterns
        query = """
        SELECT ?pattern ?purpose ?category WHERE {
            ?pattern rdf:type ?testPattern .
            ?pattern test:hasTestPurpose ?purpose .
            ?pattern test:hasTestCategory ?category .
            FILTER(?testPattern = test:SPARQLTestPattern)
        }
        """
        
        results = self.graph.query(query, 
                                 initBindings={
                                     'test': self.test
                                 })
        patterns = list(results)
        
        # Debug: Print all triples for SPARQLTestPattern
        logger.info("All triples for SPARQLTestPattern:")
        for s, p, o in self.graph.triples((None, RDF.type, self.test.SPARQLTestPattern)):
            logger.info(f"Subject: {s}, Predicate: {p}, Object: {o}")
        
        self.assertGreater(len(patterns), 0, "No test patterns found")
        logger.info(f"Found {len(patterns)} test patterns")
        
        # Verify pattern properties
        for pattern, purpose, category in patterns:
            self.assertIsNotNone(purpose, "Pattern missing purpose")
            self.assertIsNotNone(category, "Pattern missing category")
            logger.info(f"Verified pattern: {pattern} with purpose: {purpose} and category: {category}")

    def test_property_cardinality(self):
        """Test property cardinality pattern"""
        logger.info("Testing property cardinality pattern")
        
        # Query for properties with incorrect cardinality
        query = """
        SELECT ?subject ?property (COUNT(?value) as ?count)
        WHERE {
            ?shape a sh:NodeShape ;
                   sh:property ?propertyShape .
            ?propertyShape sh:path ?property ;
                          sh:minCount ?minCount ;
                          sh:maxCount ?maxCount .
            ?subject ?property ?value .
        }
        GROUP BY ?subject ?property HAVING (COUNT(?value) < ?minCount || COUNT(?value) > ?maxCount)
        """
        
        results = self.graph.query(query)
        violations = list(results)
        
        self.assertEqual(len(violations), 0, f"Found {len(violations)} cardinality violations")
        logger.info("No cardinality violations found")

    def test_process_completeness(self):
        """Test process completeness pattern"""
        logger.info("Testing process completeness pattern")
        
        # Query for incomplete processes
        query = """
        SELECT ?process WHERE {
            ?process rdf:type error:ErrorHandlingProcess .
            FILTER NOT EXISTS {
                ?process error:hasProcessStep ?step .
                ?step error:hasStepOrder ?order .
            }
        }
        """
        
        results = self.graph.query(query, 
                                 initBindings={
                                     'error': self.error
                                 })
        incomplete = list(results)
        
        self.assertEqual(len(incomplete), 0, f"Found {len(incomplete)} incomplete processes")
        logger.info("No incomplete processes found")

    def test_type_hierarchy(self):
        """Test type hierarchy pattern"""
        logger.info("Testing type hierarchy pattern")
        
        # Query for invalid type hierarchies
        query = """
        SELECT ?type ?superType WHERE {
            ?type rdfs:subClassOf ?superType .
            FILTER NOT EXISTS {
                ?type rdf:type owl:Class .
                ?superType rdf:type owl:Class .
            }
        }
        """
        
        results = self.graph.query(query)
        invalid = list(results)
        
        self.assertEqual(len(invalid), 0, f"Found {len(invalid)} invalid type hierarchies")
        logger.info("No invalid type hierarchies found")

    def test_pattern_application(self):
        """Test pattern application"""
        logger.info("Testing pattern application")
        
        # Query for pattern applications
        query = """
        SELECT ?application ?pattern ?ontology ?result WHERE {
            ?application rdf:type test:TestPatternApplication .
            ?application test:appliesPattern ?pattern .
            ?application test:targetOntology ?ontology .
            ?application test:testResult ?result .
        }
        """
        
        results = self.graph.query(query, 
                                 initBindings={
                                     'test': self.test
                                 })
        applications = list(results)
        
        self.assertGreater(len(applications), 0, "No pattern applications found")
        logger.info(f"Found {len(applications)} pattern applications")
        
        # Verify application properties
        for application, pattern, ontology, result in applications:
            self.assertIsNotNone(pattern, "Application missing pattern")
            self.assertIsNotNone(ontology, "Application missing ontology")
            self.assertIsNotNone(result, "Application missing result")
            logger.info(f"Verified application: {application} with pattern: {pattern} and result: {result}")

    def tearDown(self):
        """Clean up test environment"""
        logger.info("Cleaning up test environment")
        self.graph.close()


if __name__ == '__main__':
    unittest.main()
