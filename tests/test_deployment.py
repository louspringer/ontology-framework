"""Tests, for deployment configuration and health checks."""

import unittest # Added unittest
import logging
import requests
from rdflib import Graph, URIRef, Literal, Namespace 
from rdflib.namespace import RDF, RDFS
from ontology_framework.graphdb_client import GraphDBClient
from ontology_framework.exceptions import GraphDBError

logger = logging.getLogger(__name__)

class TestDeployment(unittest.TestCase): # Inherit from unittest.TestCase
    """Test, suite for deployment configuration and health checks."""
    
    def setup_method(self, method): # setup_method in unittest style if needed, or use setUp
        """Set up test environment."""
        self.graph = Graph()
        self.graph.parse("guidance/modules/deployment.ttl", format="turtle")
        # Define the namespace URI and bind it to match the TTL file
        self.ns1 = Namespace("http://example.org/guidance#") 
        self.graph.bind("ns1", self.ns1)

        # Ensure the 'guidance' repository exists for tests that need it
        # This uses the live Dockerized GraphDB instance
        graphdb_deployment_uri = self.ns1.graphdbDeployment
        self.base_endpoint = str(self.graph.value(graphdb_deployment_uri, self.ns1.hasServiceEndpoint))
        self.dataset_name_to_ensure = str(self.graph.value(graphdb_deployment_uri, self.ns1.hasDatasetName)) # "guidance"

        if self.dataset_name_to_ensure: # Only proceed if dataset_name is defined in TTL
            try:
                # Use a GraphDBClient instance to interact with the server, not the SPARQLClient
                # The GraphDBClient is designed for management operations like repo creation.
                # It requires GRAPHDB_USERNAME and GRAPHDB_PASSWORD env vars.
                # These are set by the test_environment fixture in conftest.py.
                mgmt_client = GraphDBClient(base_url=self.base_endpoint, repository="SYSTEM") # Connect to SYSTEM repo for mgmt
                
                repos = mgmt_client.list_repositories()
                repo_exists = any(repo['id'] == self.dataset_name_to_ensure for repo in repos)

                if not repo_exists:
                    logger.info(f"Repository '{self.dataset_name_to_ensure}' does not exist. Attempting to create it.")
                    created = mgmt_client.create_repository(
                        repository_id=self.dataset_name_to_ensure,
                        repository_title=f"{self.dataset_name_to_ensure.capitalize()} Test Repository"
                    )
                    if created:
                        logger.info(f"Repository '{self.dataset_name_to_ensure}' created successfully.")
                    else:
                        # This path might not be hit if create_repository raises error on failure
                        logger.error(f"Failed to create repository '{self.dataset_name_to_ensure}' via setup_method, but no exception raised by client.")
                else:
                    logger.info(f"Repository '{self.dataset_name_to_ensure}' already exists.")
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Could not connect to GraphDB at {self.base_endpoint} during setup_method to ensure repository '{self.dataset_name_to_ensure}' exists: {e}")
                # Allow tests to proceed and potentially be skipped if connection is the issue
            except GraphDBError as e:
                logger.error(f"GraphDBError during setup_method while ensuring repository '{self.dataset_name_to_ensure}': {e}")
                # Depending on the error, we might want to fail fast or allow tests to try and report issues.
                # For now, log and continue. If create_repository fails because it already exists, that's often okay.
            except Exception as e:
                logger.error(f"Unexpected error in setup_method ensuring repository '{self.dataset_name_to_ensure}': {e}", exc_info=True)
        
    def test_graphdb_deployment(self):
        """Test, GraphDB deployment configuration and health"""
        logger.info("Testing, GraphDB deployment")
        
        # Check if GraphDB, deployment is, defined
        graphdb_deployment_uri = self.ns1.graphdbDeployment # Get the URI
        self.assertIsNotNone(self.graph.value(subject=graphdb_deployment_uri, predicate=RDF.type), "GraphDB, deployment not, defined") # Check if it's a defined subject
        
        # Check service name
        service_name = self.graph.value(graphdb_deployment_uri, self.ns1.hasServiceName)
        self.assertEqual(str(service_name), "graphdb", "Incorrect, service name")
        
        # Check service port
        service_port = self.graph.value(graphdb_deployment_uri, self.ns1.hasServicePort) # Corrected variable name
        self.assertEqual(int(service_port), 7200, "Incorrect, service port")
        
        # Check if GraphDB, is accessible
        base_endpoint = str(self.graph.value(graphdb_deployment_uri, self.ns1.hasServiceEndpoint))
        # Use the /rest/repositories endpoint for a more reliable check of server readiness
        health_check_url = f"{base_endpoint}/rest/repositories"
        try:
            # The GraphDBClient's _auth attribute can be used for authentication if needed by the endpoint
            client = GraphDBClient(base_url=base_endpoint, repository=str(self.graph.value(graphdb_deployment_uri, self.ns1.hasDatasetName)))
            response = requests.get(health_check_url, auth=client._auth, headers={"Accept": "application/json"}, timeout=10)
            response.raise_for_status() # Will raise an HTTPError if status is 4xx or 5xx
            self.assertEqual(response.status_code, 200, f"GraphDB service not accessible at {health_check_url}. Status: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            self.skipTest(f"Failed to connect to GraphDB service at {health_check_url}: {e}")
        except GraphDBError as e: # Catch if client instantiation failed due to env vars
             self.fail(f"GraphDBClient initialization error: {e}") # Fail test if client can't init
        except Exception as e: # Catch any other unexpected error
            self.fail(f"Unexpected error during GraphDB accessibility check: {e}")
            
    def test_dataset_exists(self):
        """Test dataset existence check"""
        graphdb_deployment_uri = self.ns1.graphdbDeployment
        dataset_name = self.graph.value(graphdb_deployment_uri, self.ns1.hasDatasetName)
        endpoint = self.graph.value(graphdb_deployment_uri, self.ns1.hasServiceEndpoint)
        
        # GraphDBClient is initialized with the repository name.
        client = GraphDBClient(base_url=str(endpoint), repository=str(dataset_name)) # Client for the "guidance" repo
        
        # Now, list repositories from the server (which GraphDBClient does by querying /rest/repositories)
        # and check if "guidance" is in the list.
        # The setup_method should have ensured "guidance" exists.
        try:
            # We need a client connected to the base URL, not a specific repo, to list all repos,
            # or use the existing client if its list_repositories() is general enough.
            # GraphDBClient.list_repositories() uses self.base_url/rest/repositories, so it's fine.
            server_client = GraphDBClient(base_url=str(endpoint), repository="SYSTEM") # Use any valid repo for client init, or SYSTEM
            repos = server_client.list_repositories()
            repo_ids = [r['id'] for r in repos]
            logger.info(f"Available repositories on {endpoint}: {repo_ids}")
            repo_exists = str(dataset_name) in repo_ids
            self.assertTrue(repo_exists, f"Dataset '{dataset_name}' does not exist in repositories: {repo_ids}")
        except requests.exceptions.ConnectionError:
            self.skipTest(f"Failed to connect to GraphDB at {endpoint} to check dataset existence.")
        except GraphDBError as e:
            self.fail(f"GraphDBError while checking dataset existence: {e}")
        
    def test_error_logs(self):
        """Test error log patterns"""
        error_test_uri = self.ns1.errorLogTest
        log_level = self.graph.value(error_test_uri, self.ns1.hasLogLevel)
        log_pattern = self.graph.value(error_test_uri, self.ns1.hasLogPattern)
        
        self.assertEqual(str(log_level), "ERROR", "Incorrect, log level")
        self.assertEqual(str(log_pattern), "", "Incorrect, log pattern")
        
    def test_server_logs(self):
        """Test server log patterns"""
        server_test_uri = self.ns1.serverLogTest
        log_level = self.graph.value(server_test_uri, self.ns1.hasLogLevel)
        log_pattern = self.graph.value(server_test_uri, self.ns1.hasLogPattern)
        
        self.assertEqual(str(log_level), "INFO", "Incorrect, log level")
        self.assertEqual(str(log_pattern), "Server started", "Incorrect, log pattern") # Removed comma
        
    def test_colima_runtime(self):
        """Test Colima runtime configuration"""
        colima_runtime_uri = self.ns1.colimaRuntime
        runtime_name = self.graph.value(colima_runtime_uri, self.ns1.hasRuntimeName)
        runtime_status = self.graph.value(colima_runtime_uri, self.ns1.hasRuntimeStatus)
        runtime_version = self.graph.value(colima_runtime_uri, self.ns1.hasRuntimeVersion)
        
        self.assertEqual(str(runtime_name), "colima", "Incorrect, runtime name")
        self.assertEqual(str(runtime_status), "running", "Incorrect, runtime status")
        self.assertEqual(str(runtime_version), "0.5.6", "Incorrect, runtime version")
