import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from rdflib import Graph, Namespace, RDF, Literal

from ontology_framework.modules.config_change_detector import ConfigChangeDetector

class TestConfigChangeDetector(unittest.TestCase):
    """Test suite for ConfigChangeDetector."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.ttl"
        self.history_file = Path(self.temp_dir) / "logs/config_changes.json"
        # Initial configuration content using RDFLib
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
        # Initialize detector with custom paths
        self.detector = ConfigChangeDetector(str(self.config_file))
        self.detector.history_file = self.history_file
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initial_detection(self):
        """Test initial configuration detection."""
        change = self.detector.detect_changes()
        
        self.assertIsNotNone(change)
        self.assertEqual(change['type'], 'initial')
        self.assertIn('host', change['config'])
        self.assertEqual(change['config']['host'], 'http://localhost:7200')
    
    def test_no_changes(self):
        """Test when no changes are made."""
        # Initial detection
        self.detector.detect_changes()
        
        # Check again without changes
        change = self.detector.detect_changes()
        self.assertIsNone(change)
    
    def test_modified_config(self):
        """Test detection of modified configuration."""
        # Initial detection
        self.detector.detect_changes()
        # Modify configuration using RDFLib
        g = Graph()
        NS1 = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
        RDFS_NS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        g.bind("ns1", NS1)
        g.bind("rdfs", RDFS_NS)
        config = NS1.ServerConfiguration
        g.add((config, RDF.type, NS1.ServerConfiguration))
        g.add((config, RDFS_NS.label, Literal("Modified Configuration")))
        g.add((config, NS1.host, Literal("http://modified-host:7200")))
        g.add((config, NS1.repository, Literal("test")))
        g.serialize(destination=str(self.config_file), format="turtle")
        change = self.detector.detect_changes()
        
        self.assertIsNotNone(change)
        self.assertEqual(change['type'], 'update')
        self.assertIn('modified', change['changes'])
        self.assertIn('host', change['changes']['modified'])
        self.assertEqual(change['changes']['modified']['host']['new'], 
                       'http://modified-host:7200')
    
    def test_added_property(self):
        """Test detection of added properties."""
        # Initial detection
        self.detector.detect_changes()
        # Add new property using RDFLib
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
        g.add((config, NS1.newProperty, Literal("new value")))
        g.serialize(destination=str(self.config_file), format="turtle")
        change = self.detector.detect_changes()
        
        self.assertIsNotNone(change)
        self.assertIn('added', change['changes'])
        self.assertIn('newProperty', change['changes']['added'])
    
    def test_removed_property(self):
        """Test detection of removed properties."""
        # Initial detection
        self.detector.detect_changes()
        # Remove a property using RDFLib
        g = Graph()
        NS1 = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
        RDFS_NS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        g.bind("ns1", NS1)
        g.bind("rdfs", RDFS_NS)
        config = NS1.ServerConfiguration
        g.add((config, RDF.type, NS1.ServerConfiguration))
        g.add((config, RDFS_NS.label, Literal("Test Configuration")))
        g.add((config, NS1.host, Literal("http://localhost:7200")))
        # repository property removed
        g.serialize(destination=str(self.config_file), format="turtle")
        change = self.detector.detect_changes()
        
        self.assertIsNotNone(change)
        self.assertIn('removed', change['changes'])
        self.assertIn('repository', change['changes']['removed'])
    
    def test_history_persistence(self):
        """Test that change history is properly persisted."""
        # Make multiple changes
        self.detector.detect_changes()  # Initial
        # Modified config using RDFLib
        g = Graph()
        NS1 = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
        RDFS_NS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        g.bind("ns1", NS1)
        g.bind("rdfs", RDFS_NS)
        config = NS1.ServerConfiguration
        g.add((config, RDF.type, NS1.ServerConfiguration))
        g.add((config, RDFS_NS.label, Literal("Modified Configuration")))
        g.add((config, NS1.host, Literal("http://modified-host:7200")))
        g.add((config, NS1.repository, Literal("test")))
        g.serialize(destination=str(self.config_file), format="turtle")
        self.detector.detect_changes()
        # Create new detector instance
        new_detector = ConfigChangeDetector(str(self.config_file))
        new_detector.history_file = self.history_file
        history = new_detector.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['type'], 'initial')
        self.assertEqual(history[1]['type'], 'update')
    
    def test_export_history_ttl(self):
        """Test exporting history as TTL."""
        # Make some changes
        self.detector.detect_changes()  # Initial
        # Modified config using RDFLib
        g = Graph()
        NS1 = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
        RDFS_NS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        g.bind("ns1", NS1)
        g.bind("rdfs", RDFS_NS)
        config = NS1.ServerConfiguration
        g.add((config, RDF.type, NS1.ServerConfiguration))
        g.add((config, RDFS_NS.label, Literal("Modified Configuration")))
        g.add((config, NS1.host, Literal("http://modified-host:7200")))
        g.add((config, NS1.repository, Literal("test")))
        g.serialize(destination=str(self.config_file), format="turtle")
        self.detector.detect_changes()
        # Export and verify TTL
        ttl = self.detector.export_history_ttl()
        self.assertIsInstance(ttl, str)
        # Verify TTL can be parsed
        g = Graph()
        g.parse(data=ttl, format='turtle')
        self.assertTrue(len(g) > 0)
    
    def test_invalid_config_file(self):
        """Test handling of invalid configuration file."""
        # Write invalid TTL
        self.config_file.write_text("INVALID TTL CONTENT")
        change = self.detector.detect_changes()
        self.assertIsNone(change)
    
    def test_missing_config_file(self):
        """Test handling of missing configuration file."""
        self.config_file.unlink()
        
        change = self.detector.detect_changes()
        self.assertIsNone(change)

if __name__ == '__main__':
    unittest.main() 