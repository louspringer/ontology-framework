import unittest
from unittest.mock import patch, MagicMock
import os
from pathlib import Path
import tempfile
from datetime import datetime
from rdflib import Graph, Namespace, RDF, Literal

from ontology_framework.modules.graphdb_validator import GraphDBValidator

class TestGraphDBValidator(unittest.TestCase):
    """Test suite for GraphDBValidator."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.ttl"
        # Create config TTL using RDFLib
        g = Graph()
        NS1 = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
        RDFS_NS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        g.bind("ns1", NS1)
        g.bind("rdfs", RDFS_NS)
        config = NS1.ServerConfiguration
        g.add((config, RDF.type, NS1.ServerConfiguration))
        g.add((config, RDFS_NS.label, Literal("Test Configuration")))
        g.add((config, NS1.host, Literal("http://localhost:7200")))
        g.add((config, NS1.repository, Literal("test")))
        g.serialize(destination=str(self.config_file), format="turtle")
        # Initialize validator
        self.validator = GraphDBValidator(str(self.config_file))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
        if hasattr(self.validator, 'log_file') and self.validator.log_file.exists():
            self.validator.log_file.unlink()
    
    def test_init(self):
        """Test validator initialization."""
        self.assertEqual(self.validator.config_file, self.config_file)
        self.assertEqual(len(self.validator.validation_history), 0)
        self.assertTrue(self.validator.log_file.parent.exists())
    
    def test_validate_config_file_not_found(self):
        """Test validation when config file doesn't exist."""
        validator = GraphDBValidator("nonexistent.ttl")
        is_valid, report = validator.validate_config()
        
        self.assertFalse(is_valid)
        self.assertEqual(len(report['checks']), 1)
        self.assertEqual(report['checks'][0]['name'], 'config_file_exists')
        self.assertFalse(report['checks'][0]['passed'])
    
    def test_validate_invalid_ttl_syntax(self):
        """Test validation with invalid TTL syntax."""
        # Create config with invalid syntax
        self.config_file.write_text("@prefix ns1: <https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#>\nINVALID SYNTAX")
        is_valid, report = self.validator.validate_config()
        self.assertFalse(is_valid)
        self.assertTrue(any(check['name'] == 'ttl_syntax' and not check['passed'] 
                          for check in report['checks']))
    
    @patch('requests.get')
    def test_validate_endpoint_connectivity(self, mock_get):
        """Test GraphDB endpoint connectivity validation."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        is_valid, report = self.validator.validate_config()
        
        self.assertTrue(is_valid)
        self.assertTrue(any(check['name'] == 'endpoint_connectivity' and check['passed']
                          for check in report['checks']))
        
        # Test connection failure
        mock_get.side_effect = Exception("Connection failed")
        is_valid, report = self.validator.validate_config()
        
        self.assertFalse(is_valid)
        self.assertTrue(any(check['name'] == 'endpoint_connectivity' and not check['passed']
                          for check in report['checks']))
    
    def test_validation_history(self):
        """Test validation history tracking."""
        self.validator.validate_config()
        self.validator.validate_config()
        
        history = self.validator.get_validation_history()
        self.assertEqual(len(history), 2)
        self.assertTrue(all(isinstance(report['timestamp'], str) for report in history))
    
    def test_export_validation_report(self):
        """Test validation report export."""
        is_valid, report = self.validator.validate_config()
        
        # Test TTL export
        ttl_output = self.validator.export_validation_report(report)
        self.assertIsInstance(ttl_output, str)
        
        # Verify TTL can be parsed
        g = Graph()
        g.parse(data=ttl_output, format='turtle')
        self.assertTrue(len(g) > 0)
        
        # Test invalid format
        with self.assertRaises(ValueError):
            self.validator.export_validation_report(report, format='invalid')
    
    def test_environment_override(self):
        """Test GraphDB URL environment override."""
        test_url = "http://test-graphdb:7200"
        with patch.dict(os.environ, {'GRAPHDB_URL': test_url}):
            is_valid, report = self.validator.validate_config()
            self.assertTrue(any(check['message'].endswith(test_url)
                              for check in report['checks']))

if __name__ == '__main__':
    unittest.main() 