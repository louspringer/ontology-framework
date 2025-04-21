"""
Module for managing test setup and configurations.
"""

from typing import Dict, List, Optional
from pathlib import Path
import yaml
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL

class TestSetupManager:
    """Class for managing test setup and configurations."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "tests/config/test_config.yaml"
        self.config = self._load_config()
        self.test_graph = Graph()
        
    def _load_config(self) -> Dict:
        """Load test configuration from YAML file."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            return {}
            
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
            
    def setup_test_ontology(self) -> Graph:
        """Set up a test ontology with sample data."""
        # Bind common namespaces
        self.test_graph.bind("rdf", RDF)
        self.test_graph.bind("rdfs", RDFS)
        self.test_graph.bind("owl", OWL)
        self.test_graph.bind("test", URIRef("http://example.org/test#"))
        
        # Create test classes
        test_class = URIRef("http://example.org/test#TestClass")
        self.test_graph.add((test_class, RDF.type, OWL.Class))
        self.test_graph.add((test_class, RDFS.label, Literal("Test Class")))
        self.test_graph.add((test_class, RDFS.comment, Literal("A class for testing")))
        
        # Create test properties
        test_prop = URIRef("http://example.org/test#testProperty")
        self.test_graph.add((test_prop, RDF.type, OWL.ObjectProperty))
        self.test_graph.add((test_prop, RDFS.label, Literal("test property")))
        self.test_graph.add((test_prop, RDFS.domain, test_class))
        
        # Create test individuals
        test_individual = URIRef("http://example.org/test#testIndividual")
        self.test_graph.add((test_individual, RDF.type, test_class))
        self.test_graph.add((test_individual, RDFS.label, Literal("test individual")))
        
        return self.test_graph
        
    def get_test_data(self, data_type: str) -> List[Dict]:
        """Get test data from configuration."""
        return self.config.get('test_data', {}).get(data_type, [])
        
    def create_test_shapes(self) -> Graph:
        """Create SHACL shapes for testing."""
        shapes_graph = Graph()
        shapes_graph.bind("sh", URIRef("http://www.w3.org/ns/shacl#"))
        
        # Add basic shape for TestClass
        test_shape = URIRef("http://example.org/test#TestShape")
        shapes_graph.add((test_shape, RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape")))
        shapes_graph.add((test_shape, URIRef("http://www.w3.org/ns/shacl#targetClass"), 
                         URIRef("http://example.org/test#TestClass")))
        
        return shapes_graph
        
    def cleanup(self) -> None:
        """Clean up test resources."""
        self.test_graph = Graph()
        # Additional cleanup if needed 