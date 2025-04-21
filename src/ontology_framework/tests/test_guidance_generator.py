import unittest
import tempfile
from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode, Namespace, XSD, RDF, RDFS, OWL, SH
from ontology_framework.modules.guidance_generator import GuidanceGenerator, generate_guidance_ontology

class TestGuidanceGenerator(unittest.TestCase):
    """Test cases for the guidance generator."""
    
    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = Path(self.temp_dir) / "guidance.ttl"
        self.generator = GuidanceGenerator()
        
    def test_generate_ontology(self) -> None:
        """Test ontology generation."""
        # Generate the ontology
        self.generator.generate(self.output_path)
        
        # Load the generated file
        graph = Graph()
        graph.parse(self.output_path, format="turtle")
        
        # Check ontology metadata
        self.assertTrue((URIRef(self.generator.base.GuidanceOntology), RDF.type, OWL.Ontology) in graph)
        self.assertTrue((URIRef(self.generator.base.GuidanceOntology), RDFS.label, Literal("Guidance Ontology", lang="en")) in graph)
        
        # Check Python validation classes
        self.assertTrue((URIRef(self.generator.base.PythonValidation), RDF.type, OWL.Class) in graph)
        self.assertTrue((URIRef(self.generator.base.TypeAnnotation), RDF.type, OWL.Class) in graph)
        self.assertTrue((URIRef(self.generator.base.RDFLibIntegration), RDF.type, OWL.Class) in graph)
        
        # Check validation properties
        self.assertTrue((URIRef(self.generator.base.hasTypeAnnotation), RDF.type, OWL.DatatypeProperty) in graph)
        self.assertTrue((URIRef(self.generator.base.usesRDFLib), RDF.type, OWL.ObjectProperty) in graph)
        
        # Check SHACL shapes
        shapes = list(graph.subjects(RDF.type, SH.NodeShape))
        self.assertTrue(len(shapes) >= 2)  # At least Python and RDFLib shapes
        
        # Check validation instances
        self.assertTrue((URIRef(self.generator.base.StrictTypeAnnotation), RDF.type, URIRef(self.generator.base.TypeAnnotation)) in graph)
        self.assertTrue((URIRef(self.generator.base.GraphIntegration), RDF.type, URIRef(self.generator.base.RDFLibIntegration)) in graph)
        
    def test_generate_guidance_ontology(self) -> None:
        """Test the convenience function."""
        generate_guidance_ontology(self.output_path)
        
        # Load the generated file
        graph = Graph()
        graph.parse(self.output_path, format="turtle")
        
        # Check basic structure
        self.assertTrue((URIRef(self.generator.base.GuidanceOntology), RDF.type, OWL.Ontology) in graph)
        self.assertTrue((URIRef(self.generator.base.PythonValidation), RDF.type, OWL.Class) in graph)
        
    def test_custom_base_uri(self) -> None:
        """Test with custom base URI."""
        custom_uri = "http://example.org/guidance#"
        generator = GuidanceGenerator(custom_uri)
        generator.generate(self.output_path)
        
        # Load the generated file
        graph = Graph()
        graph.parse(self.output_path, format="turtle")
        
        # Check namespace binding
        self.assertEqual(str(graph.namespace_manager.store.namespace("")), custom_uri)
        
    def tearDown(self) -> None:
        """Clean up test environment."""
        if self.output_path.exists():
            self.output_path.unlink()
        Path(self.temp_dir).rmdir()

if __name__ == "__main__":
    unittest.main() 