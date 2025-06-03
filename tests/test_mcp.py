# !/usr/bin/env python3
"""Test suite for MCP (Maintenance Control Protocol)."""

from typing import Dict, List, Any
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from ontology_framework.mcp.maintenance_server import MaintenanceServer
from ontology_framework.mcp.maintenance_config import MaintenanceConfig
from ontology_framework.mcp.maintenance_prompts import MaintenancePrompts
from rdflib import Graph, URIRef
from ontology_framework.modules.mcp_config import MCPConfig
from ontology_framework.modules.ontology_dependency_analyzer import OntologyDependencyAnalyzer

class TestMaintenanceServer(unittest.TestCase):
    """Test cases for maintenance server."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MaintenanceConfig()
        self.prompts = MaintenancePrompts()
        self.server = MaintenanceServer(self.config, self.prompts)
        self.test_ontology = Path("tests/data/test_ontology.ttl")

    def test_server_initialization(self):
        """Test server initialization."""
        self.assertIsNotNone(self.server)
        self.assertEqual(self.server.status, "idle")
        self.assertIsNotNone(self.server.config)
        self.assertIsNotNone(self.server.prompts)

    def test_load_ontology(self):
        """Test ontology loading."""
        graph = Graph()
        graph.parse(data="""
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# > .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix ex: <http://example.org/> .

            ex:TestClass a owl:Class ;
                rdfs:label "Test Class" ;
                rdfs:comment "A test class" .
        """, format="turtle")
        
        self.server.load_ontology(graph)
        self.assertIsNotNone(self.server.ontology)
        self.assertEqual(len(self.server.ontology), len(graph))

    def test_maintenance_cycle(self):
        """Test maintenance cycle execution."""
        self.server.start_maintenance()
        self.assertEqual(self.server.status, "running")
        
        self.server.execute_cycle()
        self.assertIn(self.server.status, ["completed", "error"])
        
        cycle_results = self.server.get_cycle_results()
        self.assertIsNotNone(cycle_results)
        self.assertIn("start_time", cycle_results)
        self.assertIn("end_time", cycle_results)
        self.assertIn("status", cycle_results)

    def test_maintenance_scheduling(self):
        """Test maintenance scheduling."""
        schedule_time = datetime.now() + timedelta(hours=1)
        self.server.schedule_maintenance(schedule_time)
        
        schedule = self.server.get_schedule()
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule["next_run"], schedule_time)

    def test_maintenance_interruption(self):
        """Test maintenance interruption."""
        self.server.start_maintenance()
        self.assertEqual(self.server.status, "running")
        
        self.server.interrupt_maintenance()
        self.assertEqual(self.server.status, "interrupted")
        
        cycle_results = self.server.get_cycle_results()
        self.assertEqual(cycle_results["status"], "interrupted")

    def test_maintenance_config(self):
        """Test maintenance configuration."""
        new_config = MaintenanceConfig()
        new_config.set_option("max_retries", 5)
        new_config.set_option("timeout", 300)
        
        self.server.update_config(new_config)
        current_config = self.server.get_config()
        
        self.assertEqual(current_config.get_option("max_retries"), 5)
        self.assertEqual(current_config.get_option("timeout"), 300)

    def test_maintenance_prompts(self):
        """Test maintenance prompts."""
        prompt_result = self.server.execute_prompt("test_prompt")
        self.assertIsNotNone(prompt_result)
        self.assertIn("status", prompt_result)
        self.assertIn("response", prompt_result)

    def test_error_handling(self):
        """Test error handling."""
        # Simulate an error condition
        self.server.ontology = None
        
        with self.assertRaises(ValueError):
            self.server.execute_cycle()
        
        self.assertEqual(self.server.status, "error")
        
        error_log = self.server.get_error_log()
        self.assertGreater(len(error_log), 0)

    def test_dependency_analysis(self):
        """Test dependency analysis."""
        analyzer = OntologyDependencyAnalyzer()
        self.server.set_analyzer(analyzer)
        
        graph = Graph()
        graph.parse(data="""
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# > .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix ex: <http://example.org/> .

            ex:ClassA a owl:Class .
            ex:ClassB a owl:Class ;
                rdfs:subClassOf ex:ClassA .
        """, format="turtle")
        
        self.server.load_ontology(graph)
        dependencies = self.server.analyze_dependencies()
        
        self.assertIsNotNone(dependencies)
        self.assertGreater(len(dependencies), 0)

    def test_mcp_config_integration(self):
        """Test MCP config integration."""
        mcp_config = MCPConfig()
        mcp_config.set_validation_level("strict")
        
        self.server.set_mcp_config(mcp_config)
        current_mcp_config = self.server.get_mcp_config()
        
        self.assertEqual(current_mcp_config.validation_level, "strict")

    def tearDown(self):
        """Clean up test fixtures."""
        self.server = None
        self.config = None
        self.prompts = None

if __name__ == '__main__':
    unittest.main() 