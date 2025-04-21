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
        
        # Set up Fuseki server
        cls._setup_fuseki()
        
        # Create test client
        cls.client = SparqlClient(
            base_url="http://localhost:3030",
            server_type="fuseki",  # Specify server type as Fuseki
            auth=None  # Default Fuseki setup doesn't require auth
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
    def _setup_fuseki(cls):
        """Set up Apache Jena Fuseki server using Docker."""
        logger.info("Setting up Fuseki server via Docker")
        
        # Check if Docker is running
        try:
            subprocess.run(["docker", "info"], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.error("Docker is not running or not installed")
            raise RuntimeError("Docker is required for running tests")
            
        # Check if Fuseki container is already running
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=fuseki", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                check=True
            )
            if "fuseki" in result.stdout:
                logger.info("Fuseki container is already running")
                return
        except subprocess.CalledProcessError:
            pass
            
        # Start Fuseki container
        try:
            subprocess.run([
                "docker", "run", "-d",
                "--name", "fuseki",
                "-p", "3030:3030",
                "-e", "ADMIN_PASSWORD=admin",
                "-e", "ENABLE_DATA_WRITE=true",
                "-e", "ENABLE_UPDATE=true",
                "stain/jena-fuseki:latest"
            ], check=True)
            logger.info("Started Fuseki container")
            
            # Wait for Fuseki to be ready
            time.sleep(15)  # Increased wait time to ensure Fuseki is ready
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start Fuseki container: {e}")
            raise RuntimeError("Failed to start Fuseki container")
            
    @classmethod
    def _teardown_fuseki(cls):
        """Clean up Fuseki Docker container."""
        try:
            subprocess.run(["docker", "stop", "fuseki"], capture_output=True)
            subprocess.run(["docker", "rm", "fuseki"], capture_output=True)
            logger.info("Cleaned up Fuseki container")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to clean up Fuseki container: {e}")

    @classmethod
    def _setup_mock_server(cls):
        """Set up a mock SPARQL server for testing."""
        from flask import Flask, request, jsonify
        import threading
        
        app = Flask(__name__)
        cls.mock_server = app
        
        @app.route('/$/datasets', methods=['POST'])
        def create_dataset():
            return jsonify({"status": "ok"}), 201
            
        @app.route('/$/datasets/<dataset>', methods=['DELETE'])
        def delete_dataset(dataset):
            return jsonify({"status": "ok"}), 200
            
        @app.route('/<dataset>/data', methods=['POST'])
        def load_data(dataset):
            return jsonify({"status": "ok"}), 200
            
        @app.route('/<dataset>/sparql', methods=['POST'])
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
            kwargs={'port': 3030, 'debug': False}
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
            
        # Clean up Fuseki container
        cls._teardown_fuseki()
        
        logger.info("Test environment cleaned up")

if __name__ == "__main__":
    unittest.main() 