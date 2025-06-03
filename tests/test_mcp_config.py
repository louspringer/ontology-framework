"""Test suite for MCP configuration."""

import unittest
from pathlib import Path
import tempfile
import json
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD
from ontology_framework.modules.mcp_config import (
    MCPConfig,
    MCPValidator,
    MCPConfigError,
    MCPValidationError
)


class TestMCPConfig(unittest.TestCase):
    """Test cases for MCP configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        config_data = {
            "validation": {
                "enabled": True,
                "strict": True,
                "rules": {
                    "phaseOrder": True,
                    "contextRequired": True,
                    "serverConfigRequired": True
                }
            },
            "mcpServers": {
                "datapilot": {
                    "url": "http://localhost:8000",
                    "type": "ontology",
                    "timeout": 30
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "mcp.log"
            }
        }
        json.dump(config_data, self.temp_config)
        self.temp_config.close()
        
        self.config = MCPConfig(Path(self.temp_config.name))
        self.config.load()
        self.validator = MCPValidator(self.config)
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        self.assertIsNotNone(self.config)
        self.assertIsInstance(self.config.config, dict)
        self.assertIn("validation", self.config.config)
    
    def test_config_validation(self):
        """Test configuration validation."""
        validation_rules = self.config.get_validation_rules()
        self.assertIsInstance(validation_rules, dict)
        self.assertTrue(validation_rules["enabled"])
    
    def test_server_config(self):
        """Test server configuration retrieval."""
        server_config = self.config.get_server_config("datapilot")
        self.assertIsInstance(server_config, dict)
        self.assertEqual(server_config["url"], "http://localhost:8000")
        self.assertEqual(server_config["type"], "ontology")
        self.assertEqual(server_config["timeout"], 30)
    
    def test_invalid_server_config(self):
        """Test invalid server configuration."""
        with self.assertRaises(MCPConfigError):
            self.config.get_server_config("nonexistent")
    
    def test_ontology_validation(self):
        """Test ontology validation."""
        # Create a simple valid ontology
        graph = Graph()
        graph.parse(data="""
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix ex: <http://example.org/> .

            ex:TestClass a owl:Class ;
                rdfs:label "Test Class" ;
                rdfs:comment "A test class" .
        """, format="turtle")
        
        # Note: This will return True if pyshacl is not installed (which is expected)
        result = self.validator.validate_ontology(graph)
        self.assertTrue(result)
    
    def test_phase_order_validation(self):
        """Test phase order validation."""
        valid_phases = ["discovery", "plan", "do", "check", "act"]
        result = self.validator.validate_phase_order(valid_phases)
        self.assertTrue(result)
        
        invalid_phases = ["plan", "discovery", "do", "check", "act"]
        result = self.validator.validate_phase_order(invalid_phases)
        self.assertFalse(result)
    
    def test_context_validation(self):
        """Test context validation."""
        # Create temporary files for testing
        ontology_file = tempfile.NamedTemporaryFile(suffix='.ttl', delete=False)
        target_file = tempfile.NamedTemporaryFile(suffix='.ttl', delete=False)
        ontology_file.close()
        target_file.close()
        
        valid_context = {
            "ontology_path": ontology_file.name,
            "target_files": [target_file.name],
            "server_config": {"url": "http://localhost:8000", "type": "ontology", "timeout": 30}
        }
        result = self.validator.validate_context(valid_context)
        self.assertTrue(result)
        
        # Clean up
        Path(ontology_file.name).unlink()
        Path(target_file.name).unlink()
    
    def test_server_config_validation(self):
        """Test server configuration validation."""
        valid_config = {
            "url": "http://localhost:8000",
            "type": "ontology",
            "timeout": 30
        }
        result = self.validator.validate_server_config(valid_config)
        self.assertTrue(result)
        
        invalid_config = {
            "url": "invalid-url",
            "type": "ontology",
            "timeout": -1
        }
        result = self.validator.validate_server_config(invalid_config)
        self.assertFalse(result)
    
    def tearDown(self):
        """Clean up test fixtures."""
        Path(self.temp_config.name).unlink()
        self.config = None
        self.validator = None


if __name__ == '__main__':
    unittest.main() 