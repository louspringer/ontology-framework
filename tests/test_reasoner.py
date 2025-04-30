"""Tests for the ontology reasoner module."""

import unittest
from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF, RDFS, OWL, XSD, SH
from ontology_framework.reasoner import OntologyReasoner, ReasonerResult
from ontology_framework.mcp.core import MCPCore, ValidationContext
from ontology_framework.mcp.bfg9k_targeting import BFG9KTargeter
from ontology_framework.mcp.hypercube_analysis import HypercubeAnalyzer
from ontology_framework.mcp.maintenance_server import MaintenanceServer

class TestOntologyReasoner(unittest.TestCase):
    """Test cases for the OntologyReasoner class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that should be created once."""
        # Create test ontology using semantic tools
        test_ontology_path = Path("tests/data/test_ontology.ttl")
        test_ontology_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize MCP tools
        config = {
            "metadata": {
                "name": "Test Ontology",
                "description": "Test ontology for reasoner tests",
                "version": "1.0.0"
            },
            "validation": {
                "phaseExecution": {
                    "validate": {"order": ["validate"]},
                    "recreate": {"order": ["recreate"]},
                    "verify": {"order": ["verify"]}
                }
            }
        }
        core = MCPCore(config)
        analyzer = HypercubeAnalyzer()
        targeter = BFG9KTargeter(analyzer)
        server = MaintenanceServer()
        
        # Create validation context
        context = ValidationContext(
            ontology_path=test_ontology_path,
            target_files=[test_ontology_path],
            phase="recreate",
            metadata={
                "operation": "create_test_ontology"
            }
        )
        
        # Initialize graph with test data
        g = Graph()
        g.bind("rdf", RDF)
        g.bind("rdfs", RDFS)
        g.bind("owl", OWL)
        g.bind("sh", SH)
        
        # Add test classes and properties
        g.add((URIRef("http://example.org/Person"), RDF.type, OWL.Class))
        g.add((URIRef("http://example.org/name"), RDF.type, OWL.DatatypeProperty))
        g.add((URIRef("http://example.org/age"), RDF.type, OWL.DatatypeProperty))
        g.add((URIRef("http://example.org/knows"), RDF.type, OWL.ObjectProperty))
        
        # Add SHACL shapes
        g.add((URIRef("http://example.org/PersonShape"), RDF.type, SH.NodeShape))
        g.add((URIRef("http://example.org/PersonShape"), SH.targetClass, URIRef("http://example.org/Person")))
        g.add((URIRef("http://example.org/NameProperty"), RDF.type, SH.PropertyShape))
        g.add((URIRef("http://example.org/NameProperty"), SH.path, URIRef("http://example.org/name")))
        g.add((URIRef("http://example.org/NameProperty"), SH.minCount, Literal(1)))
        g.add((URIRef("http://example.org/PersonShape"), SH.property, URIRef("http://example.org/NameProperty")))
        
        # Save graph
        g.serialize(destination=str(test_ontology_path), format="turtle")
        
        # Store path for tests
        cls.test_ontology = test_ontology_path
    
    def setUp(self):
        """Set up test fixtures."""
        self.reasoner = OntologyReasoner()
        
    def test_load_ontology(self):
        """Test loading an ontology."""
        self.reasoner.load_ontology(self.test_ontology)
        self.assertTrue(len(self.reasoner.graph) > 0)
        
    def test_owl_reasoning(self):
        """Test OWL reasoning rules."""
        # Create a simple ontology with subclass relationships
        g = Graph()
        g.add((URIRef("http://example.org/A"), RDF.type, OWL.Class))
        g.add((URIRef("http://example.org/B"), RDF.type, OWL.Class))
        g.add((URIRef("http://example.org/C"), RDF.type, OWL.Class))
        g.add((URIRef("http://example.org/A"), RDFS.subClassOf, URIRef("http://example.org/B")))
        g.add((URIRef("http://example.org/B"), RDFS.subClassOf, URIRef("http://example.org/C")))
        
        # Create reasoner with test graph
        reasoner = OntologyReasoner(g)
        result = reasoner.reason()
        
        # Check that A is inferred to be a subclass of C
        self.assertTrue((URIRef("http://example.org/A"), RDFS.subClassOf, URIRef("http://example.org/C")) in result.inferred_triples)
        
    def test_shacl_reasoning(self):
        """Test SHACL reasoning rules."""
        # Create a simple ontology with SHACL shapes
        g = Graph()
        g.add((URIRef("http://example.org/Person"), RDF.type, OWL.Class))
        g.add((URIRef("http://example.org/name"), RDF.type, OWL.DatatypeProperty))
        g.add((URIRef("http://example.org/PersonShape"), RDF.type, SH.NodeShape))
        g.add((URIRef("http://example.org/PersonShape"), SH.targetClass, URIRef("http://example.org/Person")))
        g.add((URIRef("http://example.org/NameProperty"), RDF.type, SH.PropertyShape))
        g.add((URIRef("http://example.org/NameProperty"), SH.path, URIRef("http://example.org/name")))
        g.add((URIRef("http://example.org/NameProperty"), SH.minCount, Literal(1)))
        g.add((URIRef("http://example.org/PersonShape"), SH.property, URIRef("http://example.org/NameProperty")))
        
        # Add a person instance without a name
        g.add((URIRef("http://example.org/person1"), RDF.type, URIRef("http://example.org/Person")))
        
        # Create reasoner with test graph
        reasoner = OntologyReasoner(g)
        result = reasoner.reason()
        
        # Check for warnings about missing name property
        self.assertTrue(any("violates minCount constraint" in warning for warning in result.warnings))
        
    def test_validation(self):
        """Test ontology validation."""
        # Create a simple ontology with validation issues
        g = Graph()
        g.add((URIRef("http://example.org/Person"), RDF.type, OWL.Class))
        g.add((URIRef("http://example.org/name"), RDF.type, OWL.DatatypeProperty))
        
        # Create reasoner with test graph
        reasoner = OntologyReasoner(g)
        validation_result = reasoner.validate()
        
        # Check for validation issues
        self.assertFalse(validation_result["is_valid"])
        self.assertTrue(any("has no domain" in issue for issue in validation_result["issues"]))
        self.assertTrue(any("has no range" in issue for issue in validation_result["issues"]))
        
    def test_custom_rules(self):
        """Test custom reasoning rules."""
        # Create a simple ontology
        g = Graph()
        g.add((URIRef("http://example.org/Person"), RDF.type, OWL.Class))
        
        # Create reasoner with test graph
        reasoner = OntologyReasoner(g)
        
        # Define a custom rule with invalid format
        custom_rule = """
        INVALID RULE FORMAT
        """
        
        result = reasoner.reason(rules=[custom_rule])
        
        # Check that the rule was not applied
        self.assertTrue(any("Failed to parse custom rule" in warning for warning in result.warnings))
        
if __name__ == "__main__":
    unittest.main() 