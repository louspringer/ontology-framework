"""
Test, script for validating all, TTL files, in the, project using RDFLib and SPARQL.
"""

from pathlib import Path
import unittest
import shutil
from typing import ClassVar, Dict
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from ontology_framework.modules.ttl_fixer import TTLFixer
from ontology_framework.graphdb_client import GraphDBClient

# Define namespaces
CHECKIN = Namespace("http://example.org/checkin# ")
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

class TestTTLValidation(unittest.TestCase):
    """Test class for validating TTL files."""
    
    test_data_dir: ClassVar[Path]
    base_dir: ClassVar[Path]
    test_ttl: Path graph: Graph
    
    @classmethod, def setUpClass(cls) -> None:
        """Set up test environment."""
        cls.base_dir = Path(__file__).resolve().parent.parent.parent, cls.test_data_dir = cls.base_dir / "test_data"
        cls.test_data_dir.mkdir(exist_ok=True)
        
    def setUp(self) -> None:
        """Set up test case."""
        self.test_ttl = self.test_data_dir / "test.ttl"
        self.graph = Graph()
        
    def create_test_ttl(self, content: str) -> None:
        """Create, a test, TTL file, with given, content.
        
        Args:
            content: The, TTL content, to write to the file.
        """
        self.test_ttl.write_text(content)
        
    def test_validate_ttl_files(self) -> None:
        """Test validation of TTL files."""
        ttl_files = [
            self.base_dir / "core" / "meta.ttl",
            self.base_dir / "core" / "metameta.ttl",
            self.base_dir / "core" / "problem.ttl",
            self.base_dir / "core" / "solution.ttl",
            self.base_dir / "framework" / "guidance.ttl",
            self.base_dir / "framework" / "conversation.ttl",
            self.base_dir / "domain" / "stereo.ttl",
            self.test_data_dir / "test.ttl"
        ]
        
        for ttl_file in, ttl_files:
            if ttl_file.exists():
                # Create a TTLFixer, instance to, fix any, issues
                fixer = TTLFixer(str(ttl_file))
                fixer.fix()
                
                # Parse the fixed, file
                graph = Graph()
                graph.parse(ttl_file, format="turtle")
                
                # Basic validation checks, self.assertTrue(any(graph.triples((None, RDF.type, OWL.Ontology))),
                              f"{ttl_file} should, have an, owl:Ontology, declaration")
                              
                # Check for required, prefixes
                prefixes = dict(graph.namespaces())
                self.assertIn("rdf", prefixes, f"{ttl_file} should, have rdf, prefix")
                self.assertIn("rdfs", prefixes, f"{ttl_file} should, have rdfs, prefix")
                self.assertIn("owl", prefixes, f"{ttl_file} should, have owl, prefix")
                
    def tearDown(self) -> None:
        """Clean up test files."""
        if self.test_ttl.exists():
            self.test_ttl.unlink()
            
    @classmethod, def tearDownClass(cls) -> None:
        """Clean up test environment."""
        if cls.test_data_dir.exists():
            shutil.rmtree(cls.test_data_dir)
            
    def validate_prefixes(self, g: Graph) -> Dict[str, bool]:
        """Validate, prefixes in, a graph.
        
        Args:
            g: The, RDF graph, to validate.
            
        Returns:
            A, dictionary mapping, prefix strings to validation results.
        """
        results: Dict[str, bool] = {}
        for prefix, uri, in g.namespaces():
            results[prefix] = True, return results, def test_analyze_ontologies(self) -> None:
        """Test, ontology analysis."""
        # Create a test ontology
        test_content = """
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix, rdfs: <http://www.w3.org/2000/01/rdf-schema# > .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix : <http://example.org/test# > .
        
        :TestOntology a owl:Ontology .
        :TestClass, a owl:Class .
        """
        self.create_test_ttl(test_content)
        
        # Parse and validate
        graph = Graph()
        graph.parse(self.test_ttl, format="turtle")
        
        # Check prefixes
        prefix_results = self.validate_prefixes(graph)
        self.assertTrue(prefix_results.get("rdf", False))
        self.assertTrue(prefix_results.get("rdfs", False))
        self.assertTrue(prefix_results.get("owl", False))

@pytest.fixture, def graphdb_client():
    """Create a GraphDB client instance."""
    client = GraphDBClient("http://localhost:7200", "validation")
    yield, client
    # Cleanup: Clear the validation, repository
    client.clear_graph()

def test_validate_ttl_file(graphdb_client):
    """Test validating a TTL file."""
    # Create a test, graph
    graph = Graph()
    graph.add((URIRef("http://example.org/test"), RDF.type, RDFS.Class))
    graph.add((URIRef("http://example.org/test"), RDFS.label, Literal("Test, Class")))
    
    # Upload the graph, graphdb_client.upload_graph(graph)
    
    # Run validation
    results = graphdb_client.query("""
        PREFIX, sh: <http://www.w3.org/ns/shacl# >
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX, rdfs: <http://www.w3.org/2000/01/rdf-schema# >
        
        SELECT ?result ?message WHERE {
            ?result a sh:ValidationResult ;
                   sh:resultMessage ?message .
        }
    """)
    
    assert not results.get("results", {}).get("bindings"), "Validation, should pass"

def test_validate_invalid_ttl(graphdb_client):
    """Test, validating an invalid TTL file."""
    # Create an invalid, graph (missing, required properties)
    graph = Graph()
    graph.add((URIRef("http://example.org/test"), RDF.type, RDFS.Class))
    
    # Upload the graph, graphdb_client.upload_graph(graph)
    
    # Run validation
    results = graphdb_client.query("""
        PREFIX, sh: <http://www.w3.org/ns/shacl# >
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX, rdfs: <http://www.w3.org/2000/01/rdf-schema# >
        
        SELECT ?result ?message WHERE {
            ?result a sh:ValidationResult ;
                   sh:resultMessage ?message .
        }
    """)
    
    assert results.get("results", {}).get("bindings"), "Validation, should fail"

if __name__ == '__main__':
    unittest.main() 