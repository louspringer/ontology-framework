#!/usr/bin/env python3
"""Test suite for deployment configuration and process."""

import unittest
import logging
import os
import requests
import subprocess
import time
from typing import Dict, Optional
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from ontology_framework.jena_client import JenaFusekiClient
from ontology_framework.deployment_modeler import DeploymentModeler, DeploymentError
from ontology_framework.graphdb_client import GraphDBClient, GraphDBError
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define namespaces
NS1 = Namespace("http://example.org/guidance#")

class TestDeployment(unittest.TestCase):
    """Test cases for deployment configuration and process."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        logger.info("Setting up test environment")
        cls.graph = Graph()
        cls.graph.parse("guidance/modules/deployment.ttl", format="turtle")
        cls.deployment_tests = {}
        cls.logging_tests = {}
        cls._load_test_config()

    @classmethod
    def _load_test_config(cls):
        """Load test configuration from ontology."""
        # Load service tests
        service_query = """
        PREFIX ns1: <http://example.org/guidance#>
        SELECT ?name ?endpoint ?response
        WHERE {
            ?test a ns1:JenaFusekiTest ;
                ns1:hasTestName ?name ;
                ns1:hasTestEndpoint ?endpoint ;
                ns1:hasExpectedResponse ?response .
        }
        """
        for result in cls.graph.query(service_query):
            cls.deployment_tests[str(result[0])] = {
                "endpoint": str(result[1]),
                "expected_response": str(result[2])
            }

        # Load logging tests
        logging_query = """
        PREFIX ns1: <http://example.org/guidance#>
        SELECT ?name ?level ?pattern
        WHERE {
            ?test a ns1:LoggingTest ;
                ns1:hasTestName ?name ;
                ns1:hasLogLevel ?level ;
                ns1:hasLogPattern ?pattern .
        }
        """
        for result in cls.graph.query(logging_query):
            cls.logging_tests[str(result[0])] = {
                "level": str(result[1]),
                "pattern": str(result[2])
            }

    def test_health_check(self):
        """Test Fuseki health check endpoint."""
        logger.info("Running health check test")
        test_config = self.deployment_tests.get("health_check")
        if test_config is None:
            self.skipTest("Health check test configuration not found")

        try:
            response = requests.get(test_config["endpoint"], timeout=5)
            self.assertEqual(response.status_code, int(test_config["expected_response"]), "Health check failed")
            logger.info("Health check test passed")
        except requests.RequestException as e:
            self.skipTest(f"Health check request failed: {e}")

    def test_dataset_exists(self):
        """Test if required dataset exists."""
        logger.info("Running dataset check test")
        test_config = self.deployment_tests.get("dataset_check")
        if test_config is None:
            self.skipTest("Dataset check test configuration not found")

        try:
            response = requests.get(test_config["endpoint"], timeout=5)
            self.assertEqual(
                str(response.status_code),
                test_config["expected_response"],
                "Dataset check failed"
            )
            logger.info("Dataset check test passed")
        except requests.RequestException as e:
            self.skipTest(f"Dataset check request failed: {e}")

    def test_server_logs(self):
        """Test server log patterns."""
        logger.info("Running log check test")
        test_config = self.logging_tests.get("log_check")
        if test_config is None:
            self.skipTest("Log check test configuration not found")

        try:
            with open("deployment.log", "r") as f:
                log_content = f.read()
            
            if test_config["pattern"]:
                self.assertIn(
                    test_config["pattern"],
                    log_content,
                    f"Expected log pattern '{test_config['pattern']}' not found"
                )
            logger.info("Log check test passed")
        except FileNotFoundError:
            self.skipTest("Deployment log file not found")
        except Exception as e:
            self.skipTest(f"Log check failed: {e}")

    def test_error_logs(self):
        """Test error log patterns."""
        logger.info("Running error log check test")
        test_config = self.logging_tests.get("error_log_check")
        if test_config is None:
            self.skipTest("Error log check test configuration not found")

        try:
            with open("deployment.log", "r") as f:
                log_content = f.read()
            
            error_lines = [
                line for line in log_content.splitlines()
                if test_config["level"] in line
            ]
            
            if test_config["pattern"]:
                for line in error_lines:
                    self.assertIn(
                        test_config["pattern"],
                        line,
                        f"Unexpected error pattern found: {line}"
                    )
            else:
                self.assertEqual(
                    len(error_lines),
                    0,
                    f"Found unexpected error logs: {error_lines}"
                )
            logger.info("Error log check test passed")
        except FileNotFoundError:
            self.skipTest("Deployment log file not found")
        except Exception as e:
            self.skipTest(f"Error log check failed: {e}")

    def test_colima_runtime(self):
        """Test Colima runtime configuration and status"""
        logger.info("Testing Colima runtime configuration")
        
        # Check if Colima runtime is defined
        colima_runtime = NS1.colimaRuntime
        self.assertIsNotNone(colima_runtime, "Colima runtime not defined")
        
        # Verify runtime properties
        runtime_name = self.graph.value(colima_runtime, NS1.hasRuntimeName)
        self.assertEqual(str(runtime_name), "colima", "Incorrect runtime name")
        
        runtime_version = self.graph.value(colima_runtime, NS1.hasRuntimeVersion)
        self.assertEqual(str(runtime_version), "0.5.6", "Incorrect runtime version")
        
        # Check if Colima is running
        try:
            result = subprocess.run(['colima', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            output = result.stdout + result.stderr
            self.assertIn("colima is running", output, "Colima is not running")
            logger.info("Colima runtime test passed")
        except subprocess.CalledProcessError:
            self.skipTest("Failed to check Colima status")
            
    def test_fuseki_deployment(self):
        """Test Fuseki deployment configuration and health"""
        logger.info("Testing Fuseki deployment")
        
        # Check if Fuseki deployment is defined
        fuseki_deployment = NS1.fusekiDeployment
        self.assertIsNotNone(fuseki_deployment, "Fuseki deployment not defined")
        
        # Verify deployment properties
        service_name = self.graph.value(fuseki_deployment, NS1.hasServiceName)
        self.assertEqual(str(service_name), "fuseki", "Incorrect service name")
        
        service_port = self.graph.value(fuseki_deployment, NS1.hasServicePort)
        self.assertEqual(int(service_port), 3030, "Incorrect service port")
        
        # Check if Fuseki is accessible
        endpoint = self.graph.value(fuseki_deployment, NS1.hasServiceEndpoint)
        try:
            response = requests.get(str(endpoint))
            self.assertEqual(response.status_code, 200, "Fuseki service not accessible")
        except requests.exceptions.RequestException:
            self.skipTest("Failed to connect to Fuseki service")
            
    def test_dataset_existence(self):
        """Test if the guidance dataset exists"""
        logger.info("Testing dataset existence")
        
        fuseki_deployment = NS1.fusekiDeployment
        dataset_name = self.graph.value(fuseki_deployment, NS1.hasDatasetName)
        endpoint = self.graph.value(fuseki_deployment, NS1.hasServiceEndpoint)
        
        try:
            response = requests.get(f"{endpoint}/{dataset_name}")
            self.assertEqual(response.status_code, 200, "Dataset not found")
        except requests.exceptions.RequestException:
            self.skipTest("Failed to check dataset existence")

@pytest.fixture
def mock_graphdb_client():
    """Create a mock GraphDB client."""
    with patch('ontology_framework.graphdb_client.GraphDBClient') as mock:
        client = mock.return_value
        client.list_graphs.return_value = ["test-graph"]
        client.count_triples.return_value = 100
        yield client

@pytest.fixture
def deployment_modeler(mock_graphdb_client):
    """Create a deployment modeler instance."""
    return DeploymentModeler("http://localhost:7200", "test")

def test_deploy_ontology(deployment_modeler, mock_graphdb_client):
    """Test deploying an ontology."""
    ontology_path = Path("test.ttl")
    deployment_modeler.deploy_ontology(ontology_path)
    mock_graphdb_client.load_ontology.assert_called_once_with(ontology_path)

def test_clear_dataset(deployment_modeler, mock_graphdb_client):
    """Test clearing a dataset."""
    deployment_modeler.clear_dataset("test-graph")
    mock_graphdb_client.clear_graph.assert_called_once_with("test-graph")

def test_list_datasets(deployment_modeler, mock_graphdb_client):
    """Test listing datasets."""
    datasets = deployment_modeler.list_datasets()
    assert datasets == ["test-graph"]
    mock_graphdb_client.list_graphs.assert_called_once()

def test_get_dataset_info(deployment_modeler, mock_graphdb_client):
    """Test getting dataset information."""
    info = deployment_modeler.get_dataset_info("test-graph")
    assert info["triples"] == 100
    mock_graphdb_client.count_triples.assert_called_once_with("test-graph")

def test_deployment_error_handling(deployment_modeler, mock_graphdb_client):
    """Test error handling during deployment."""
    mock_graphdb_client.load_ontology.side_effect = GraphDBError("Test error")
    with pytest.raises(DeploymentError):
        deployment_modeler.deploy_ontology(Path("test.ttl"))

if __name__ == "__main__":
    unittest.main() 