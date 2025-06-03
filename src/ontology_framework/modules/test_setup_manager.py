# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: [current version from guidance.ttl]
# Behavioral-Profile: ClaudeReflector

"""Module for managing test setup and configuration."""

from typing import Dict, List, Optional
from pathlib import Path
import yaml
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL

class TestSetupManager:
    """Class for managing test setup and configuration."""
    
    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize the test setup manager.
        
        Args:
            config_path: Optional path to test configuration file
        """
        self.config_path = config_path or Path("tests/config.yaml")
        self.config: Dict = {}
        self.load_config()
        
    def load_config(self) -> None:
        """Load test configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                "test_data": {
                    "ontologies": [],
                    "instances": []
                }
            }
            
    def get_test_graphs(self) -> List[Graph]:
        """Get all test graphs.
        
        Returns:
            List of RDF graphs for testing
        """
        graphs = []
        for ontology in self.config.get("test_data", {}).get("ontologies", []):
            g = Graph()
            g.parse(ontology["path"], format=ontology.get("format", "turtle"))
            graphs.append(g)
        return graphs
        
    def get_test_instances(self) -> List[Dict]:
        """Get all test instances.
        
        Returns:
            List of test instance configurations
        """
        return self.config.get("test_data", {}).get("instances", []) 