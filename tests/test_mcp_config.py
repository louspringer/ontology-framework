"""Test suite for MCP configuration and validation."""

import unittest
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH

from src.ontology_framework.modules.mcp_config import MCPConfig, MCPValidator, MCPConfigError, MCPValidationError

class TestMCPConfig(unittest.TestCase):
    """Test cases for MCP configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_path = Path("src/ontology_framework/config/mcp.json")
        self.config = MCPConfig(self.config_path)
        self.config.load()
        
    def test_load_config(self):
        """Test loading configuration from file."""
        self.assertIn("mcpServers", self.config.config)
        self.assertIn("validation", self.config.config)
        self.assertIn("logging", self.config.config)
        
    def test_get_server_config(self):
        """Test getting server configuration."""
        server_config = self.config.get_server_config("datapilot")
        self.assertEqual(server_config["url"], "http://localhost:8080/sse")
        self.assertEqual(server_config["type"], "sse")
        self.assertEqual(server_config["timeout"], 30)
        
    def test_get_validation_rules(self):
        """Test getting validation rules."""
        rules = self.config.get_validation_rules()
        self.assertTrue(rules["enabled"])
        self.assertFalse(rules["strict"])
        self.assertTrue(rules["rules"]["phaseOrder"])
        
    def test_invalid_server(self):
        """Test getting configuration for invalid server."""
        with self.assertRaises(MCPConfigError):
            self.config.get_server_config("invalid_server")

class TestMCPValidator(unittest.TestCase):
    """Test cases for MCP validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        config = MCPConfig(Path("src/ontology_framework/config/mcp.json"))
        config.load()
        self.validator = MCPValidator(config)
        
    def test_validate_phase_order(self):
        """Test phase order validation."""
        valid_phases = ["discovery", "plan", "do", "check", "act"]
        invalid_phases = ["plan", "do", "check", "act"]
        
        self.assertTrue(self.validator.validate_phase_order(valid_phases))
        self.assertFalse(self.validator.validate_phase_order(invalid_phases))
        
    def test_validate_context(self):
        """Test context validation."""
        valid_context = {
            "ontology_path": "models/mcp_prompt.ttl",
            "target_files": ["src/ontology_framework/modules/mcp_prompt.py"],
            "server_config": {"url": "http://localhost:8080/sse", "type": "sse", "timeout": 30}
        }
        invalid_context = {
            "ontology_path": "nonexistent.ttl",
            "target_files": []
        }
        
        self.assertTrue(self.validator.validate_context(valid_context))
        self.assertFalse(self.validator.validate_context(invalid_context))
        
    def test_validate_server_config(self):
        """Test server configuration validation."""
        valid_config = {
            "url": "http://localhost:8080/sse",
            "type": "sse",
            "timeout": 30
        }
        invalid_config = {
            "url": "not a url",
            "type": "sse"
        }
        
        self.assertTrue(self.validator.validate_server_config(valid_config))
        self.assertFalse(self.validator.validate_server_config(invalid_config))
        
    def test_validate_ontology(self):
        """Test ontology validation with SHACL shapes."""
        # Create a test graph with a simple ontology
        data_graph = Graph()
        ex = Namespace("http://example.org/")
        
        # Add a class and an instance
        data_graph.add((ex.Person, RDF.type, OWL.Class))
        data_graph.add((ex.john, RDF.type, ex.Person))
        
        # Add a SHACL shape
        shape_graph = Graph()
        person_shape = URIRef("http://example.org/PersonShape")
        shape_graph.add((person_shape, RDF.type, SH.NodeShape))
        shape_graph.add((person_shape, SH.targetClass, ex.Person))
        
        # Test validation
        try:
            self.assertTrue(self.validator.validate_ontology(data_graph, shape_graph))
        except ImportError:
            self.skipTest("pyshacl not installed")

if __name__ == '__main__':
    unittest.main() 