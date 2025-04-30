#!/usr/bin/env python3
"""Test suite for SPARQL client."""

import unittest
import logging
import os
import tempfile
import time
import subprocess
import shutil
from pathlib import Path
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, OWL
from ontology_framework.sparql_client import SparqlClient, SparqlClientError
import pytest
from unittest.mock import Mock, patch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define namespaces
NS1 = Namespace("http://example.org/guidance#")

class TestSparqlClient(unittest.TestCase):
    """Test cases for SparqlClient class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        logger.info("Setting up test environment")
        
        # Set up GraphDB server
        cls._setup_graphdb()
        
        # Create test client
        cls.client = SparqlClient(
            base_url="http://localhost:7200",
            server_type="graphdb"
        )
        
        cls.test_dataset = "test_ontology"
        cls.test_ontology = """
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        
        <http://example.org/Person>
            a rdfs:Class ;
            rdfs:label "Person" .
            
        <http://example.org/PersonShape>
            a sh:NodeShape ;
            sh:targetClass <http://example.org/Person> ;
            sh:property [
                sh:path <http://example.org/name> ;
                sh:minCount 1 ;
                sh:maxCount 1 ;
                sh:datatype xsd:string
            ] .
        """
        cls._create_test_ontology()
        
    @classmethod
    def _setup_graphdb(cls):
        """Set up GraphDB server using Docker."""
        logger.info("Setting up GraphDB server via Docker")
        
        # Check if Docker is running
        try:
            subprocess.run(["docker", "info"], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.error("Docker is not running or not installed")
            raise RuntimeError("Docker is required for running tests")
            
        # Check if GraphDB container is already running
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=graphdb", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True
            )
            if "graphdb" in result.stdout:
                logger.info("GraphDB container is already running")
                return
        except subprocess.CalledProcessError:
            pass
            
        # Start GraphDB container
        try:
            subprocess.run([
                "docker-compose", "up", "-d"
            ], check=True)
            logger.info("Started GraphDB container")
            
            # Wait for GraphDB to be ready
            time.sleep(15)  # Increased wait time to ensure GraphDB is ready
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start GraphDB container: {e}")
            raise RuntimeError("Failed to start GraphDB container")
            
    @classmethod
    def _teardown_graphdb(cls):
        """Clean up GraphDB Docker container."""
        try:
            subprocess.run(["docker-compose", "down"], capture_output=True)
            logger.info("Cleaned up GraphDB container")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to clean up GraphDB container: {e}")

    @classmethod
    def _setup_mock_server(cls):
        """Set up a mock SPARQL server for testing."""
        from flask import Flask, request, jsonify
        import threading
        
        app = Flask(__name__)
        cls.mock_server = app
        
        @app.route('/rest/repositories', methods=['POST'])
        def create_dataset():
            return jsonify({"status": "ok"}), 201
            
        @app.route('/rest/repositories/<dataset>', methods=['DELETE'])
        def delete_dataset(dataset):
            return jsonify({"status": "ok"}), 200
            
        @app.route('/repositories/<dataset>/statements', methods=['POST'])
        def load_data(dataset):
            return jsonify({"status": "ok"}), 200
            
        @app.route('/repositories/<dataset>', methods=['POST'])
        def execute_query(dataset):
            return jsonify({
                "results": {
                    "bindings": [
                        {"label": {"value": "Person"}}
                    ]
                }
            }), 200
            
        # Start the server in a separate thread
        cls.server_thread = threading.Thread(
            target=app.run,
            kwargs={'port': 7200, 'debug': False}
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)  # Wait for server to start
        logger.info("Mock server started")

    @classmethod
    def _create_test_ontology(cls):
        """Create a test ontology file."""
        cls.test_ontology_file = tempfile.NamedTemporaryFile(suffix=".ttl", delete=False)
        g = Graph()
        g.add((NS1.TestClass, RDF.type, OWL.Class))
        g.add((NS1.TestClass, RDFS.label, Literal("Test Class")))
        g.add((NS1.TestClass, RDFS.comment, Literal("A test class")))
        g.serialize(destination=cls.test_ontology_file.name, format="turtle")
        logger.info(f"Created test ontology: {cls.test_ontology_file.name}")

    def setUp(self):
        """Set up before each test."""
        # Create test dataset if it doesn't exist
        if not self.client.dataset_exists(self.test_dataset):
            self.assertTrue(self.client.create_dataset(self.test_dataset))
            
    def tearDown(self):
        """Clean up after each test."""
        # Delete test dataset
        if self.client.dataset_exists(self.test_dataset):
            self.assertTrue(self.client.delete_dataset(self.test_dataset))
            
    def test_create_dataset(self):
        """Test dataset creation."""
        # Delete dataset if it exists
        if self.client.dataset_exists(self.test_dataset):
            self.assertTrue(self.client.delete_dataset(self.test_dataset))
            
        # Create new dataset
        self.assertTrue(self.client.create_dataset(self.test_dataset))
        
    def test_delete_dataset(self):
        """Test dataset deletion."""
        # Ensure dataset exists
        if not self.client.dataset_exists(self.test_dataset):
            self.assertTrue(self.client.create_dataset(self.test_dataset))
            
        # Delete dataset
        self.assertTrue(self.client.delete_dataset(self.test_dataset))
        
    def test_load_ontology(self):
        """Test ontology loading."""
        # Create temporary file with test ontology
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
            f.write(self.test_ontology)
            temp_path = f.name
            
        try:
            # Load ontology
            self.assertTrue(self.client.load_ontology(temp_path, self.test_dataset))
            
            # Verify data was loaded
            query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            ASK {
                ?class a rdfs:Class ;
                       rdfs:label "Person" .
            }
            """
            results = self.client.execute_query(query, self.test_dataset)
            self.assertTrue(results)
            
        finally:
            os.unlink(temp_path)
            
    def test_execute_query(self):
        """Test SPARQL query execution."""
        # Load test ontology
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
            f.write(self.test_ontology)
            temp_path = f.name
            
        try:
            self.client.load_ontology(temp_path, self.test_dataset)
            
            # Test SELECT query
            query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?class ?label
            WHERE {
                ?class a rdfs:Class .
                ?class rdfs:label ?label .
            }
            """
            results = self.client.execute_query(query, self.test_dataset)
            self.assertTrue(len(results) > 0)
            self.assertEqual(results[0]['label']['value'], 'Person')
            
            # Test CONSTRUCT query
            construct_query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            CONSTRUCT {
                ?class rdfs:label ?label
            }
            WHERE {
                ?class a rdfs:Class .
                ?class rdfs:label ?label .
            }
            """
            graph = self.client.execute_query(construct_query, self.test_dataset)
            self.assertTrue(len(graph) > 0)
            
        finally:
            os.unlink(temp_path)
            
    def test_validate_ontology(self):
        """Test ontology validation."""
        # Load test ontology
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
            f.write(self.test_ontology)
            temp_path = f.name
            
        try:
            self.client.load_ontology(temp_path, self.test_dataset)
            
            # Test validation
            validation_results = self.client.validate_ontology(self.test_dataset)
            self.assertTrue(isinstance(validation_results, list))
            self.assertEqual(len(validation_results), 0)  # No validation errors
            
            # Test validation with invalid data
            invalid_ontology = """
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix sh: <http://www.w3.org/ns/shacl#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
            
            <http://example.org/InvalidPerson>
                a rdfs:Class ;
                rdfs:label "Invalid Person" .
            """
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
                f.write(invalid_ontology)
                invalid_path = f.name
                
            try:
                self.client.load_ontology(invalid_path, self.test_dataset)
                validation_results = self.client.validate_ontology(self.test_dataset)
                self.assertTrue(len(validation_results) > 0)  # Should have validation errors
            finally:
                os.unlink(invalid_path)
                
        finally:
            os.unlink(temp_path)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        logger.info("Cleaning up test environment")
        
        # Clean up test files
        if hasattr(cls, 'test_ontology_file'):
            os.unlink(cls.test_ontology_file.name)
            
        # Clean up GraphDB container
        cls._teardown_graphdb()
        
        logger.info("Test environment cleaned up")

@pytest.fixture
def sparql_client():
    return SparqlClient()

def test_dataset_exists(sparql_client):
    with patch('requests.Session.get') as mock_get:
        mock_get.return_value.status_code = 200
        assert sparql_client.dataset_exists("test") is True
        
        mock_get.return_value.status_code = 404
        assert sparql_client.dataset_exists("test") is False

def test_create_dataset(sparql_client):
    with patch('requests.Session.put') as mock_put:
        mock_put.return_value.status_code = 201
        assert sparql_client.create_dataset("test") is True
        
        mock_put.return_value.status_code = 405
        with pytest.raises(SparqlClientError):
            sparql_client.create_dataset("test")

def test_delete_dataset(sparql_client):
    with patch('requests.Session.delete') as mock_delete:
        mock_delete.return_value.status_code = 204
        assert sparql_client.delete_dataset("test") is True
        
        mock_delete.return_value.status_code = 404
        with pytest.raises(SparqlClientError):
            sparql_client.delete_dataset("test")

def test_execute_query(sparql_client):
    with patch('requests.Session.post') as mock_post:
        mock_post.return_value.json.return_value = {
            'results': {
                'bindings': [
                    {'var1': {'value': 'value1'}},
                    {'var2': {'value': 'value2'}}
                ]
            }
        }
        results = sparql_client.execute_query("SELECT * WHERE { ?s ?p ?o }", "test")
        assert len(results) == 2
        assert results[0]['var1'] == 'value1'
        assert results[1]['var2'] == 'value2'

def test_load_ontology(sparql_client):
    with patch('builtins.open', Mock(return_value=Mock(read=Mock(return_value=b"test data")))):
        with patch('requests.Session.post') as mock_post:
            mock_post.return_value.status_code = 200
            assert sparql_client.load_ontology("test.ttl", "test") is True
            
            mock_post.return_value.status_code = 400
            with pytest.raises(SparqlClientError):
                sparql_client.load_ontology("test.ttl", "test")

def test_validate_ontology(sparql_client):
    with patch('ontology_framework.sparql_client.SparqlClient.execute_query') as mock_execute:
        mock_execute.return_value = [
            {
                'shape': 'shape1',
                'targetClass': 'class1',
                'property': 'prop1',
                'minCount': '1',
                'maxCount': '1',
                'datatype': 'string'
            }
        ]
        results = sparql_client.validate_ontology("test")
        assert len(results) == 1
        assert results[0]['shape'] == 'shape1'

if __name__ == "__main__":
    unittest.main() 