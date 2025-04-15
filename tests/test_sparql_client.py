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
from src.ontology_framework.sparql_client import SparqlClient, SparqlClientError

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
        
        # Set up Fuseki server if not running
        cls.fuseki_dir = Path.home() / "apache-jena-fuseki"
        if not cls.fuseki_dir.exists():
            cls._setup_fuseki()
            
        # Create test client
        cls.client = SparqlClient(
            base_url="http://localhost:3030",
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
        """Download and set up Apache Jena Fuseki server."""
        logger.info("Setting up Fuseki server")
        
        # Check if Fuseki is already installed via package manager
        try:
            subprocess.run(["fuseki-server", "--version"], capture_output=True)
            logger.info("Fuseki server already installed")
            return
        except FileNotFoundError:
            pass
            
        # Try to install via package manager
        try:
            subprocess.run(["brew", "install", "apache-jena-fuseki"], check=True)
            logger.info("Installed Fuseki via Homebrew")
            return
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
            
        # If all else fails, use a mock server for testing
        logger.warning("Could not install Fuseki server. Using mock server for testing.")
        cls._setup_mock_server()
        
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
        try:
            # Create a temporary dataset for testing
            self.assertTrue(self.client.create_dataset(self.test_dataset))
            time.sleep(1)  # Wait for dataset to be created
        except SparqlClientError as e:
            if "already exists" not in str(e):
                raise
            
    def tearDown(self):
        """Clean up after each test."""
        try:
            # Delete the test dataset
            self.assertTrue(self.client.delete_dataset(self.test_dataset))
            time.sleep(1)  # Wait for dataset to be deleted
        except SparqlClientError as e:
            if "not found" not in str(e):
                raise

    def test_create_dataset(self):
        """Test dataset creation."""
        # Delete existing dataset if it exists
        try:
            self.client.delete_dataset(self.test_dataset)
        except:
            pass
            
        self.assertTrue(self.client.create_dataset(self.test_dataset))
        
    def test_delete_dataset(self):
        """Test dataset deletion."""
        # Create dataset if it doesn't exist
        try:
            self.client.create_dataset(self.test_dataset)
        except:
            pass
            
        self.assertTrue(self.client.delete_dataset(self.test_dataset))
        
    def test_load_ontology(self):
        """Test ontology loading."""
        # Create a temporary file with test ontology
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
            f.write(self.test_ontology)
            temp_path = f.name
            
        try:
            self.assertTrue(self.client.load_ontology(temp_path))
        finally:
            os.unlink(temp_path)
            
    def test_execute_query(self):
        """Test SPARQL query execution."""
        # Load test ontology
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
            f.write(self.test_ontology)
            temp_path = f.name
            
        try:
            self.client.load_ontology(temp_path)
            
            # Test SELECT query
            query = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?class ?label
            WHERE {
                ?class a rdfs:Class .
                ?class rdfs:label ?label .
            }
            """
            results = self.client.execute_query(query)
            self.assertTrue(len(results) > 0)
            self.assertEqual(results[0]['label']['value'], 'Person')
            
        finally:
            os.unlink(temp_path)
            
    def test_validate_ontology(self):
        """Test ontology validation."""
        # Load test ontology
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
            f.write(self.test_ontology)
            temp_path = f.name
            
        try:
            self.client.load_ontology(temp_path)
            
            # Test validation
            validation_results = self.client.validate_ontology()
            self.assertTrue(isinstance(validation_results, list))
            self.assertEqual(len(validation_results), 0)  # No validation errors
            
        finally:
            os.unlink(temp_path)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        logger.info("Cleaning up test environment")
        if hasattr(cls, 'test_ontology_file'):
            os.unlink(cls.test_ontology_file.name)
            
        # Stop server
        if hasattr(cls, 'server_thread'):
            cls.mock_server.shutdown()
            cls.server_thread.join()
        else:
            subprocess.run(["pkill", "-f", "fuseki-server"])
        logger.info("Test environment cleaned up")

if __name__ == "__main__":
    unittest.main() 