"""Test suite for dependency model."""

import unittest
from pathlib import Path
from typing import Dict, List, Set, Optional
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL
import tempfile
import shutil
import os
import logging

from ontology_framework.dependency_model import DependencyModelGenerator, DependencyType

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
TEST = Namespace("http://example.org/test#")

class TestDependencyModelGenerator(unittest.TestCase):
    """Test cases for DependencyModelGenerator."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.ontology_path = Path(self.test_dir) / "test_ontology.ttl"
        
        # Create a simple test ontology
        self.create_test_ontology()
        
        # Initialize generator
        self.generator = DependencyModelGenerator(self.ontology_path)
    
    def tearDown(self) -> None:
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def create_test_ontology(self) -> None:
        """Create a simple test ontology."""
        g = Graph()
        
        # Bind namespaces
        g.bind("guidance", GUIDANCE)
        g.bind("test", TEST)
        
        # Add test classes
        g.add((TEST.Person, RDF.type, OWL.Class))
        g.add((TEST.Person, RDFS.label, Literal("Person")))
        g.add((TEST.Person, RDFS.comment, Literal("A person in the test ontology")))
        
        g.add((TEST.Student, RDF.type, OWL.Class))
        g.add((TEST.Student, RDFS.label, Literal("Student")))
        g.add((TEST.Student, RDFS.comment, Literal("A student in the test ontology")))
        g.add((TEST.Student, RDFS.subClassOf, TEST.Person))
        
        # Add test properties
        g.add((TEST.hasName, RDF.type, OWL.DatatypeProperty))
        g.add((TEST.hasName, RDFS.label, Literal("has name")))
        g.add((TEST.hasName, RDFS.comment, Literal("The name of a person")))
        g.add((TEST.hasName, RDFS.domain, TEST.Person))
        g.add((TEST.hasName, RDFS.range, RDFS.Literal))
        
        g.add((TEST.hasTeacher, RDF.type, OWL.ObjectProperty))
        g.add((TEST.hasTeacher, RDFS.label, Literal("has teacher")))
        g.add((TEST.hasTeacher, RDFS.comment, Literal("The teacher of a student")))
        g.add((TEST.hasTeacher, RDFS.domain, TEST.Student))
        g.add((TEST.hasTeacher, RDFS.range, TEST.Person))
        
        # Save ontology
        g.serialize(str(self.ontology_path), format="turtle")
        
        # Debug: Print all triples
        logger.debug("Ontology triples:")
        for s, p, o in g:
            logger.debug(f"{s} {p} {o}")
    
    def test_analyze_ontology(self) -> None:
        """Test ontology analysis."""
        self.generator.analyze_ontology()
        
        # Debug: Print nodes
        logger.debug("Generator nodes:")
        for uri, node in self.generator.nodes.items():
            logger.debug(f"{uri}: {node}")
        
        # Check nodes
        self.assertIn(TEST.Person, self.generator.nodes)
        self.assertIn(TEST.Student, self.generator.nodes)
        self.assertIn(TEST.hasName, self.generator.nodes)
        self.assertIn(TEST.hasTeacher, self.generator.nodes)
        
        # Check dependencies
        student_node = self.generator.nodes[TEST.Student]
        self.assertIn(self.generator.nodes[TEST.Person], student_node.dependencies)
        
        has_name_node = self.generator.nodes[TEST.hasName]
        self.assertIn(self.generator.nodes[TEST.Person], has_name_node.dependencies)
        
        has_teacher_node = self.generator.nodes[TEST.hasTeacher]
        self.assertIn(self.generator.nodes[TEST.Student], has_teacher_node.dependencies)
        self.assertIn(self.generator.nodes[TEST.Person], has_teacher_node.dependencies)
    
    def test_generate_code_types(self) -> None:
        """Test code type generation."""
        self.generator.analyze_ontology()
        types = self.generator.generate_code_types()
        
        # Debug: Print generated types
        logger.debug("Generated types:")
        for uri, type_def in types.items():
            logger.debug(f"{uri}:\n{type_def}")
        
        # Check generated types
        self.assertIn(TEST.Person, types)
        self.assertIn(TEST.Student, types)
        
        # Check Person class definition
        person_def = types[TEST.Person]
        self.assertIn("@dataclass", person_def)
        self.assertIn("class Person:", person_def)
        self.assertIn("uri: URIRef", person_def)
        self.assertIn("label: str", person_def)
        self.assertIn("description: str", person_def)
        self.assertIn("hasName: Literal", person_def)
        
        # Check Student class definition
        student_def = types[TEST.Student]
        self.assertIn("@dataclass", student_def)
        self.assertIn("class Student:", student_def)
        self.assertIn("uri: URIRef", student_def)
        self.assertIn("label: str", student_def)
        self.assertIn("description: str", student_def)
        self.assertIn("hasTeacher: URIRef", student_def)
    
    def test_save_dependency_model(self) -> None:
        """Test saving dependency model."""
        self.generator.analyze_ontology()
        
        output_path = Path(self.test_dir) / "model.json"
        self.generator.save_dependency_model(output_path)
        
        self.assertTrue(output_path.exists())
        
        # TODO: Add more detailed checks of the saved model
    
    def test_visualize_dependencies(self) -> None:
        """Test dependency visualization."""
        self.generator.analyze_ontology()
        
        output_path = Path(self.test_dir) / "graph.png"
        self.generator.visualize_dependencies(output_path)
        
        self.assertTrue(output_path.exists()) 