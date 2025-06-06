"""
Test SPARQL client functionality for the ontology framework.

This module tests SPARQL query, update, and validation operations.
"""

# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: 1.0.0
# Behavioral-Profile: ClaudeReflector

import pytest
import os
import tempfile
import logging # Added for logging in setup
from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from ontology_framework.sparql_client import SPARQLClient
from ontology_framework.graphdb_client import GraphDBClient # For setup
from ontology_framework.exceptions import GraphDBError # For setup
import requests # For setup connection errors

logger = logging.getLogger(__name__) # Added for logging

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

# Test data as a module-level constant
TEST_ONTOLOGY_CONTENT = """
@prefix : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

:TestModule a owl:Class ;
    rdfs:label "Test Module"@en ;
    rdfs:comment "A test module for validation"@en .
    
:TestInstance a :TestModule ;
    rdfs:label "Test Instance"@en ;
    rdfs:comment "A test instance"@en .
"""

@pytest.fixture
def temp_ontology_file():
    """Creates a temporary TTL file with test ontology content."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False)
    temp_file.write(TEST_ONTOLOGY_CONTENT)
    temp_file.close()
    yield temp_file.name # Provide the path to the test
    os.unlink(temp_file.name) # Cleanup after test

class TestSPARQLClient:
    # Class level setup to ensure "guidance" repo exists on live GraphDB
    # This assumes GRAPHDB_USERNAME and GRAPHDB_PASSWORD are set in env
    # and Dockerized GraphDB is running at http://localhost:7200
    BASE_URL = "http://localhost:7200"
    REPO_NAME = "guidance"

    @classmethod
    def setup_class(cls):
        """Ensure the 'guidance' repository exists before any tests run."""
        try:
            mgmt_client = GraphDBClient(base_url=cls.BASE_URL, repository="SYSTEM") # Connect to SYSTEM for mgmt
            repos = mgmt_client.list_repositories()
            if not any(repo['id'] == cls.REPO_NAME for repo in repos):
                logger.info(f"Repository '{cls.REPO_NAME}' does not exist. Creating it for TestSPARQLClient.")
                created = mgmt_client.create_repository(
                    repository_id=cls.REPO_NAME,
                    repository_title=f"{cls.REPO_NAME.capitalize()} Test Repository for SPARQLClient"
                )
                if created:
                    logger.info(f"Repository '{cls.REPO_NAME}' created successfully for TestSPARQLClient.")
                else:
                    logger.error(f"Failed to create repository '{cls.REPO_NAME}' for TestSPARQLClient (no exception).")
            else:
                logger.info(f"Repository '{cls.REPO_NAME}' already exists for TestSPARQLClient.")
        except requests.exceptions.ConnectionError as e:
            pytest.skip(f"Cannot connect to GraphDB at {cls.BASE_URL} to set up repository. Skipping SPARQLClient tests that require live DB: {e}")
        except GraphDBError as e:
            # If error is "Repository already exists", that's fine. Otherwise, raise.
            if "already exists" in str(e).lower():
                 logger.info(f"Repository '{cls.REPO_NAME}' already exists (GraphDBError caught).")
            else:
                logger.error(f"GraphDBError during TestSPARQLClient setup creating repository '{cls.REPO_NAME}': {e}")
                pytest.fail(f"GraphDBError during TestSPARQLClient setup: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during TestSPARQLClient setup: {e}", exc_info=True)
            pytest.fail(f"Unexpected error during TestSPARQLClient setup: {e}")


    def test_load_ontology(self, temp_ontology_file): # Removed mock_graphdb_server
        # This test remains focused on local parsing.
        # Initialize with base_url and repo, but operation is local.
        client = SPARQLClient(base_url=self.BASE_URL, repository=self.REPO_NAME)
        client.load_ontology(temp_ontology_file) # This parses locally into client.graph
        # To test "sending" to mock, we'd need an upload method in SPARQLClient
        # that POSTs to an import endpoint on the mock.
        # For now, this test mainly verifies local parsing.
        # The mock server's _handle_import_data just logs and returns success.
        assert len(client.graph) > 0
        
    def test_query(self, temp_ontology_file): # Removed mock_graphdb_server
        client = SPARQLClient(base_url=self.BASE_URL, repository=self.REPO_NAME)
        
        # Load TEST_ONTOLOGY_CONTENT into the live "guidance" repository
        # Ensure TEST_ONTOLOGY_CONTENT uses a unique graph or clear previous data if necessary
        # For simplicity, we assume the repo is clean or this data is distinct.
        
        # Clear default graph before inserting test data
        clear_default_query = "CLEAR DEFAULT"
        clear_result = client.update(clear_default_query)
        assert clear_result.get("status") == "success", f"Failed to clear default graph: {clear_result}"

        insert_query = f"""
        PREFIX : <{GUIDANCE}>
        PREFIX rdfs: <{RDFS}>
        PREFIX owl: <{OWL}>
        INSERT DATA {{
            {TEST_ONTOLOGY_CONTENT}
        }}
        """
        update_result = client.update(insert_query)
        assert update_result.get("status") == "success", f"Failed to load test data into default graph: {update_result}"

        # Query for data from TEST_ONTOLOGY_CONTENT from the default graph
        query = f"""
        PREFIX : <{GUIDANCE}>
        PREFIX rdfs: <{RDFS}>
        SELECT ?s ?label WHERE {{
            ?s a :TestModule ;
               rdfs:label ?label .
            FILTER(?s = :TestInstance)
        }}
        """
        results_data = client.query(query)
        
        assert "results" in results_data, f"Query results missing 'results' key: {results_data}"
        assert "bindings" in results_data["results"], f"Query results missing 'bindings' key: {results_data}"
        bindings = results_data["results"]["bindings"]
        assert len(bindings) == 1, f"Expected 1 binding, got {len(bindings)}: {bindings}"
        
        binding = bindings[0]
        assert binding['s'] == str(GUIDANCE.TestInstance), f"Unexpected subject: {binding['s']}"
        assert binding['label'] == "Test Instance", f"Unexpected label: {binding['label']}"

    def test_update(self, temp_ontology_file): # mock_graphdb_server fixture is no longer used
        client = SPARQLClient(base_url=self.BASE_URL, repository=self.REPO_NAME)
        
        # Clear default graph before inserting test data
        clear_default_query = "CLEAR DEFAULT"
        clear_result = client.update(clear_default_query)
        assert clear_result.get("status") == "success", f"Failed to clear default graph for update: {clear_result}"

        update_query = f"""
        PREFIX : <{GUIDANCE}>
        PREFIX rdfs: <{RDFS}>
        INSERT DATA {{
            :NewUpdateInstance a :TestModule ;
                             rdfs:label "New Update Instance"@en .
        }}
        """
        update_result = client.update(update_query)
        assert isinstance(update_result, dict)
        assert update_result.get("status") == "success"

        # Verify the update by querying the data from the default graph
        verify_query = f"""
        PREFIX : <{GUIDANCE}>
        PREFIX rdfs: <{RDFS}>
        SELECT ?label WHERE {{
            :NewUpdateInstance rdfs:label ?label .
        }}
        """
        verify_results = client.query(verify_query)
        assert "results" in verify_results and "bindings" in verify_results["results"], "Verification query failed to return results."
        assert len(verify_results["results"]["bindings"]) == 1, "Verification query did not find the updated triple."
        assert verify_results["results"]["bindings"][0]['label'] == "New Update Instance", "Updated data not found or incorrect."


    def test_validate(self, temp_ontology_file): # mock_graphdb_server fixture is no longer used
        # For validate, client.validate() operates on client.graph which is local.
        client = SPARQLClient(graph=Graph()) # Explicitly local graph for this test
        client.load_ontology(temp_ontology_file) 
        
        validation_result = client.validate()
        assert "conforms" in validation_result
        assert isinstance(validation_result["conforms"], bool)
        assert "results" in validation_result
        # Ensure no trailing characters or old unittest main block
