import pytest
import requests
from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL
import json
import time
from typing import Dict, Any, List
import concurrent.futures

class TestRepositoryManagement:
    """Test suite for repository management API endpoints."""
    
    @pytest.fixture
    def base_url(self) -> str:
        return "http://localhost:7200"
        
    @pytest.fixture
    def test_repository(self) -> str:
        return "test_repo"
        
    @pytest.fixture
    def repository_config(self) -> Dict[str, Any]:
        """Repository configuration using valid GraphDB parameters."""
        return {
            "id": "test_repo",
            "title": "Test Repository",
            "type": "graphdb:SailRepository",
            "params": {
                "ruleset": "owl-horst-optimized",  # Using a valid ruleset value
                "storage-folder": "storage",
                "base-URL": "http://example.org/owlim#",
                "entity-index-size": "1000000",
                "repository-type": "file-repository",
                "enable-context-index": "false",
                "enable-literal-index": "true",
                "enablePredicateList": "true",
                "in-memory-literal-properties": "true",
                "query-timeout": "0",
                "query-limit-results": "0",
                "throw-QueryEvaluationException-on-timeout": "false",
                "read-only": "false"
            }
        }

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, base_url: str, test_repository: str, repository_config: Dict[str, Any]):
        """Setup and teardown for each test."""
        # Delete repository if it exists
        try:
            requests.delete(f"{base_url}/rest/repositories/{test_repository}")
        except:
            pass

        # Setup: Create repository
        self.test_create_repository(base_url, test_repository, repository_config)
        yield
        # Teardown: Delete repository
        try:
            self.test_delete_repository(base_url, test_repository)
        except:
            pass  # Ignore cleanup errors

    def test_create_repository(self, base_url: str, test_repository: str, repository_config: Dict[str, Any]):
        """Test creating a new repository."""
        # Check if repository exists
        response = requests.get(f"{base_url}/rest/repositories")
        if response.status_code == 200:
            repositories = response.json()
            if any(repo["id"] == test_repository for repo in repositories):
                return  # Repository already exists

        # Convert config to GraphDB's expected format
        config_ttl = f"""
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rep: <http://www.openrdf.org/config/repository#> .
@prefix sr: <http://www.openrdf.org/config/repository/sail#> .
@prefix sail: <http://www.openrdf.org/config/sail#> .
@prefix graphdb: <http://www.ontotext.com/config/graphdb#> .

[] a rep:Repository ;
    rep:repositoryID "{repository_config['id']}" ;
    rdfs:label "{repository_config['title']}" ;
    rep:repositoryImpl [
        rep:repositoryType "graphdb:SailRepository" ;
        sr:sailImpl [
            sail:sailType "graphdb:Sail" ;
            graphdb:ruleset "{repository_config['params']['ruleset']}" ;
            graphdb:base-URL "{repository_config['params']['base-URL']}" ;
            graphdb:storage-folder "{repository_config['params']['storage-folder']}" ;
            graphdb:entity-index-size "{repository_config['params']['entity-index-size']}" ;
            graphdb:enable-context-index "{repository_config['params']['enable-context-index']}" ;
            graphdb:enable-literal-index "{repository_config['params']['enable-literal-index']}" ;
            graphdb:enablePredicateList "{repository_config['params']['enablePredicateList']}" ;
            graphdb:in-memory-literal-properties "{repository_config['params']['in-memory-literal-properties']}" ;
            graphdb:query-timeout "{repository_config['params']['query-timeout']}" ;
            graphdb:query-limit-results "{repository_config['params']['query-limit-results']}" ;
            graphdb:throw-QueryEvaluationException-on-timeout "{repository_config['params']['throw-QueryEvaluationException-on-timeout']}" ;
            graphdb:read-only "{repository_config['params']['read-only']}" ;
            graphdb:repository-type "{repository_config['params']['repository-type']}"
        ]
    ] .
"""
        # Create repository using the REST API
        files = {'config': ('config.ttl', config_ttl)}
        response = requests.post(
            f"{base_url}/rest/repositories",
            files=files
        )
        assert response.status_code in [201, 204], f"Failed to create repository: {response.text}"

        # Verify repository exists
        response = requests.get(f"{base_url}/rest/repositories")
        assert response.status_code == 200
        repositories = response.json()
        assert any(repo["id"] == test_repository for repo in repositories)

    def test_get_repository_info(self, base_url: str, test_repository: str) -> None:
        """Test getting repository information."""
        response = requests.get(f"{base_url}/rest/repositories/{test_repository}")
        assert response.status_code == 200
        info = response.json()
        assert info["id"] == test_repository

    def test_upload_data(self, base_url: str, test_repository: str) -> None:
        """Test uploading data to a repository."""
        data = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<http://example.org/test#TestClass> a owl:Class ;
    rdfs:label "Test Class" .
"""
        headers = {"Content-Type": "text/turtle"}
        response = requests.post(
            f"{base_url}/repositories/{test_repository}/statements",
            data=data,
            headers=headers
        )
        assert response.status_code == 204

    def test_query_data(self, base_url: str, test_repository: str) -> None:
        """Test querying data from a repository."""
        query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 100
"""
        headers = {"Accept": "application/sparql-results+json"}
        response = requests.get(
            f"{base_url}/repositories/{test_repository}",
            params={"query": query},
            headers=headers
        )
        assert response.status_code == 200
        results = response.json()
        assert "results" in results

    def test_delete_data(self, base_url: str, test_repository: str) -> None:
        """Test deleting data from a repository."""
        response = requests.delete(
            f"{base_url}/repositories/{test_repository}/statements"
        )
        assert response.status_code == 204

    def test_delete_repository(self, base_url: str, test_repository: str):
        """Test deleting a repository."""
        response = requests.delete(f"{base_url}/rest/repositories/{test_repository}")
        assert response.status_code in [200, 204], f"Failed to delete repository: {response.text}"

        # Verify repository no longer exists
        response = requests.get(f"{base_url}/rest/repositories")
        assert response.status_code == 200
        repositories = response.json()
        assert not any(repo["id"] == test_repository for repo in repositories)

    def test_repository_exists(self, base_url: str, test_repository: str) -> None:
        """Test checking if a repository exists."""
        # Check using the repositories list endpoint
        response = requests.get(f"{base_url}/rest/repositories")
        assert response.status_code == 200
        repositories = response.json()
        assert any(repo["id"] == test_repository for repo in repositories)

    def test_list_repositories(self, base_url: str) -> None:
        """Test listing all repositories."""
        response = requests.get(f"{base_url}/rest/repositories")
        assert response.status_code == 200
        repositories = response.json()
        assert isinstance(repositories, list)

    def test_clear_repository(self, base_url: str, test_repository: str) -> None:
        """Test clearing all data from a repository."""
        response = requests.delete(
            f"{base_url}/repositories/{test_repository}/statements"
        )
        assert response.status_code == 204, f"Failed to clear repository: {response.text}"

    def test_error_handling(self, base_url: str):
        """Test error handling for invalid operations."""
        # Test creating repository with invalid configuration
        invalid_config = "Invalid Configuration"
        response = requests.post(
            f"{base_url}/rest/repositories",
            data=invalid_config,
            headers={"Content-Type": "text/turtle"}
        )
        assert response.status_code in [400, 500], "Expected error for invalid repository creation"

    def test_concurrent_operations(self, base_url: str, test_repository: str, repository_config: Dict[str, Any]):
        """Test concurrent operations on the repository."""
        def upload_data(i: int):
            data = f"""
@prefix ex: <http://example.org/test#> .
ex:TestClass{i} a ex:Class .
"""
            headers = {"Content-Type": "text/turtle"}
            return requests.post(
                f"{base_url}/repositories/{test_repository}/statements",
                data=data,
                headers=headers
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(upload_data, i) for i in range(5)]
            for future in concurrent.futures.as_completed(futures):
                response = future.result()
                assert response.status_code == 204

    def test_large_data_handling(self, base_url: str, test_repository: str):
        """Test handling large amounts of data."""
        # Generate a large dataset
        triples = []
        for i in range(1000):
            triples.append(f"<http://example.org/test#Item{i}> a <http://example.org/test#Class> .")
        
        # Split data into chunks and upload
        chunk_size = 100
        for i in range(0, len(triples), chunk_size):
            chunk = triples[i:i + chunk_size]
            data = "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
            data += "\n".join(chunk)
            headers = {"Content-Type": "text/turtle"}
            response = requests.post(
                f"{base_url}/repositories/{test_repository}/statements",
                data=data,
                headers=headers
            )
            assert response.status_code == 204, f"Failed to upload chunk {i//chunk_size}: {response.text}"

    def test_repository_size(self, base_url: str, test_repository: str):
        """Test getting repository size."""
        response = requests.get(f"{base_url}/repositories/{test_repository}/size")
        assert response.status_code == 200
        # The response is a plain number, not JSON
        size = int(response.text)
        assert isinstance(size, int)
        assert size >= 0

    def test_repository_namespaces(self, base_url: str, test_repository: str):
        """Test managing repository namespaces."""
        # Get initial namespaces
        response = requests.get(
            f"{base_url}/repositories/{test_repository}/namespaces",
            headers={"Accept": "application/sparql-results+json"}
        )
        assert response.status_code == 200
        initial_namespaces = response.json()
        assert "results" in initial_namespaces

        # Add a new namespace
        test_prefix = "test"
        test_namespace = "http://example.org/test#"
        response = requests.put(
            f"{base_url}/repositories/{test_repository}/namespaces/{test_prefix}",
            data=test_namespace,
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code in [201, 204]

        # Delete the namespace
        response = requests.delete(
            f"{base_url}/repositories/{test_repository}/namespaces/{test_prefix}"
        )
        assert response.status_code in [200, 204]