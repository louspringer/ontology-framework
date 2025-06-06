import os
import tempfile
import unittest
from pathlib import Path
from scripts.namespace_dependency_mapper import NamespaceDependencyMapper
from ontology_framework.config.logging_config import setup_logging, get_logger

# Set up logging for tests
logger = get_logger(__name__)

def setup_module():
    """Set up logging before running tests."""
    setup_logging('namespace_dependency_mapper.log')

class TestNamespaceDependencyMapper(unittest.TestCase):
    """Test cases for NamespaceDependencyMapper following ontology framework rules.
    
    Tests semantic validation of namespace dependencies and migration plan generation
    in accordance with guidance.ttl requirements.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up logging for the test class."""
        logger.info("Setting up NamespaceDependencyMapper tests")
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        logger.info("Setting up test fixture")
        self.test_inventory_content = """
# Example.org Usage Inventory

## test.ttl
@prefix ex: <http://example.org/test#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

ex:Test a rdf:Class .

## test.py
from rdflib import Namespace
EX = Namespace("http://example.org/test#")
        """
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
        self.temp_file.write(self.test_inventory_content)
        self.temp_file.flush()
        self.mapper = NamespaceDependencyMapper(self.temp_file.name)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        if hasattr(self, 'temp_file'):
            os.unlink(self.temp_file.name)

    def test_parse_inventory(self):
        """Test parsing of inventory file for semantic namespace dependencies."""
        self.mapper.parse_inventory()
        
        self.assertEqual(len(self.mapper.dependencies), 2)
        self.assertIn("test.ttl", self.mapper.dependencies)
        self.assertIn("test.py", self.mapper.dependencies)
        self.assertGreater(len(self.mapper.graph.nodes), 0)

    def test_generate_migration_plan(self):
        """Test generation of semantic migration plan for namespace updates."""
        self.mapper.dependencies = {
            "test.ttl": {"ex:http://example.org/test#"},
            "test.py": {"EX:http://example.org/test#"},
            "test.md": {"ex:http://example.org/test#"}
        }
        
        plan = self.mapper.generate_migration_plan()
        
        self.assertIn("# Namespace Migration Plan", plan)
        self.assertIn("## 1. Ontology Namespaces", plan)
        self.assertIn("## 2. Python Namespaces", plan)
        self.assertIn("## 3. Documentation References", plan)
        self.assertIn("https://ontologies.louspringer.com/test/", plan)

    def test_save_migration_plan(self):
        """Test saving semantic migration plan to file."""
        self.mapper.dependencies = {
            "test.ttl": {"ex:http://example.org/test#"}
        }
        
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md',
                                                  delete=False)
        self.mapper.save_migration_plan(output_file.name)
        
        with open(output_file.name, 'r') as plan:
            content = plan.read()
            self.assertIn("# Namespace Migration Plan", content)
            self.assertIn("https://ontologies.louspringer.com/test/", content)
        
        os.unlink(output_file.name)

if __name__ == '__main__':
    unittest.main() 