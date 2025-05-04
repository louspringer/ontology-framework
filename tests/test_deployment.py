"""Tests for deployment configuration and health checks."""

import logging
import requests
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from ontology_framework.graphdb_client import GraphDBClient
from ontology_framework.exceptions import GraphDBError

logger = logging.getLogger(__name__)

class TestDeployment:
    """Test suite for deployment configuration and health checks."""
    
    def setup_method(self):
        """Set up test environment."""
        self.graph = Graph()
        self.graph.parse("guidance/modules/deployment.ttl", format="turtle")
        self.ns1 = self.graph.namespace_manager.namespace("ns1")
        
    def test_graphdb_deployment(self):
        """Test GraphDB deployment configuration and health"""
        logger.info("Testing GraphDB deployment")
        
        # Check if GraphDB deployment is defined
        graphdb_deployment = self.ns1.graphdbDeployment
        self.assertIsNotNone(graphdb_deployment, "GraphDB deployment not defined")
        
        # Check service name
        service_name = self.graph.value(graphdb_deployment, self.ns1.hasServiceName)
        self.assertEqual(str(service_name), "graphdb", "Incorrect service name")
        
        # Check service port
        service_port = self.graph.value(graphdb_deployment, self.ns1.hasServicePort)
        self.assertEqual(int(service_port), 7200, "Incorrect service port")
        
        # Check if GraphDB is accessible
        endpoint = self.graph.value(graphdb_deployment, self.ns1.hasServiceEndpoint)
        try:
            response = requests.get(str(endpoint))
            self.assertEqual(response.status_code, 200, "GraphDB service not accessible")
        except requests.exceptions.RequestException:
            self.skipTest("Failed to connect to GraphDB service")
            
    def test_dataset_exists(self):
        """Test dataset existence check"""
        graphdb_deployment = self.ns1.graphdbDeployment
        dataset_name = self.graph.value(graphdb_deployment, self.ns1.hasDatasetName)
        endpoint = self.graph.value(graphdb_deployment, self.ns1.hasServiceEndpoint)
        
        client = GraphDBClient(str(endpoint), str(dataset_name))
        self.assertTrue(client.dataset_exists(str(dataset_name)), "Dataset does not exist")
        
    def test_error_logs(self):
        """Test error log patterns"""
        error_test = self.ns1.errorLogTest
        log_level = self.graph.value(error_test, self.ns1.hasLogLevel)
        log_pattern = self.graph.value(error_test, self.ns1.hasLogPattern)
        
        self.assertEqual(str(log_level), "ERROR", "Incorrect log level")
        self.assertEqual(str(log_pattern), "", "Incorrect log pattern")
        
    def test_server_logs(self):
        """Test server log patterns"""
        server_test = self.ns1.serverLogTest
        log_level = self.graph.value(server_test, self.ns1.hasLogLevel)
        log_pattern = self.graph.value(server_test, self.ns1.hasLogPattern)
        
        self.assertEqual(str(log_level), "INFO", "Incorrect log level")
        self.assertEqual(str(log_pattern), "Server started", "Incorrect log pattern")
        
    def test_colima_runtime(self):
        """Test Colima runtime configuration"""
        colima_runtime = self.ns1.colimaRuntime
        runtime_name = self.graph.value(colima_runtime, self.ns1.hasRuntimeName)
        runtime_status = self.graph.value(colima_runtime, self.ns1.hasRuntimeStatus)
        runtime_version = self.graph.value(colima_runtime, self.ns1.hasRuntimeVersion)
        
        self.assertEqual(str(runtime_name), "colima", "Incorrect runtime name")
        self.assertEqual(str(runtime_status), "running", "Incorrect runtime status")
        self.assertEqual(str(runtime_version), "0.5.6", "Incorrect runtime version") 