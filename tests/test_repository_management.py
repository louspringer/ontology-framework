import pytest
import requests
from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL
import json
import time
from typing import Dict, Any, List
import concurrent.futures
import os
import tempfile
from httpx import AsyncClient
import asyncio
from ontology_framework.graphdb_client import GraphDBClient

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
                "ruleset": "owl-horst-optimized",
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

    @pytest.fixture
    async def client(self) -> AsyncClient:
        """Create an async HTTP client for testing."""
        async with AsyncClient(base_url="http://localhost:7200") as client:
            yield client

    @pytest.fixture
    def test_repo(self) -> str:
        """Provide a test repository name."""
        return "test_repo"

    @pytest.fixture
    def test_data(self) -> Dict[str, str]:
        """Provide test data in different formats."""
        return {
            "turtle": """
                @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
                @prefix owl: <http://www.w3.org/2002/07/owl#> .
                @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

                <http://example.org/test#TestClass> a owl:Class ;
                    rdfs:label "Test Class"@en ;
                    rdfs:comment "A test class for repository management tests"@en .
            """,
            "rdfxml": """
                <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                         xmlns:owl="http://www.w3.org/2002/07/owl#"
                         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
                    <owl:Class rdf:about="http://example.org/test#TestClass">
                        <rdfs:label xml:lang="en">Test Class</rdfs:label>
                        <rdfs:comment xml:lang="en">A test class for repository management tests</rdfs:comment>
                    </owl:Class>
                </rdf:RDF>
            """
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
        assert "title" in info
        assert "type" in info
        assert "params" in info

    async def test_upload_data(self, client: AsyncClient, test_repo: str, test_data: Dict[str, str]):
        """Test uploading data in different formats."""
        formats = {
            "turtle": "text/turtle",
            "rdfxml": "application/rdf+xml"
        }

        for format_name, content_type in formats.items():
            response = await client.post(
                f"/repositories/{test_repo}/statements",
                content=test_data[format_name],
                headers={"Content-Type": content_type}
            )
            assert response.status_code == 204, f"Failed to upload {format_name} data: {response.text}"

    async def test_query_data(self, client: AsyncClient, test_repo: str, test_data: Dict[str, str]):
        """Test querying data with different SPARQL query types."""
        # Upload test data first
        response = await client.post(
            f"/repositories/{test_repo}/statements",
            content=test_data["turtle"],
            headers={"Content-Type": "text/turtle"}
        )
        assert response.status_code == 204

        # Test SELECT query
        select_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT ?s ?p ?o WHERE { ?s ?p ?o }
        """
        response = await client.get(
            f"/repositories/{test_repo}",
            params={"query": select_query},
            headers={"Accept": "application/sparql-results+json"}
        )
        assert response.status_code == 200
        results = response.json()
        assert "results" in results
        assert "bindings" in results["results"]

        # Test CONSTRUCT query
        construct_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }
        """
        response = await client.get(
            f"/repositories/{test_repo}",
            params={"query": construct_query},
            headers={"Accept": "application/ld+json"}
        )
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

        # Test ASK query
        ask_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                ASK { <http://example.org/test#TestClass> a owl:Class }
        """
        response = await client.get(
            f"/repositories/{test_repo}",
            params={"query": ask_query},
            headers={"Accept": "application/sparql-results+json"}
        )
        assert response.status_code == 200
        results = response.json()
        assert "boolean" in results

    def test_delete_data(self, base_url: str, test_repository: str) -> None:
        """Test deleting data from a repository."""
        # Test deleting all data
        response = requests.delete(
            f"{base_url}/repositories/{test_repository}/statements"
        )
        assert response.status_code == 204

        # Test deleting specific data
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

        # Delete specific data
        response = requests.delete(
            f"{base_url}/repositories/{test_repository}/statements",
            data=data,
            headers=headers
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

        # Check using the specific repository endpoint
        response = requests.get(f"{base_url}/rest/repositories/{test_repository}")
        assert response.status_code == 200

    def test_list_repositories(self, base_url: str) -> None:
        """Test listing all repositories."""
        response = requests.get(f"{base_url}/rest/repositories")
        assert response.status_code == 200
        repositories = response.json()
        assert isinstance(repositories, list)
        for repo in repositories:
            assert "id" in repo
            assert "title" in repo
            assert "type" in repo

    def test_clear_repository(self, client):
        """Test clearing repository."""
        # Add some test data
        client.add_data("""
            @prefix ex: <http://example.org/> .
            ex:test a ex:Test .
        """)
        
        # Clear repository
        client.clear_repository()
        
        # Wait for clear to complete
        max_retries = 5
        retry_count = 0
        while retry_count < max_retries:
            count = client.count_statements()
            if count == 0:
                break
            time.sleep(1)
            retry_count += 1
            
        assert count == 0, f"Expected 0 statements but found {count}"

    def test_repository_backup_restore(self, client):
        """Test repository backup and restore."""
        # Add test data
        client.add_data("""
            @prefix ex: <http://example.org/> .
            ex:test a ex:Test .
        """)
        
        # Create backup
        backup_path = client.backup_repository()
        assert os.path.exists(backup_path)
        
        # Clear repository
        client.clear_repository()
        
        # Wait for clear to complete
        max_retries = 5
        retry_count = 0
        while retry_count < max_retries:
            count = client.count_statements()
            if count == 0:
                break
            time.sleep(1)
            retry_count += 1
            
        assert count == 0, f"Expected 0 statements but found {count}"
        
        # Restore from backup
        client.restore_repository(backup_path)
        
        # Verify data restored
        count = client.count_statements()
        assert count > 0, "Expected data to be restored"

    def test_repository_security(self, client):
        """Test repository security settings."""
        # Set security settings
        settings = {
            "readOnly": True,
            "accessControl": {
                "enabled": True,
                "rules": [
                    {
                        "principal": "admin",
                        "permissions": ["read", "write"]
                    }
                ]
            }
        }
        success = client.set_repository_settings(settings)
        assert success, "Failed to set security settings"
        
        # Verify settings
        current_settings = client.get_repository_settings()
        assert current_settings["readOnly"] == True
        assert current_settings["accessControl"]["enabled"] == True

    def test_repository_transactions(self, client):
        """Test repository transactions."""
        # Start transaction
        tx_id = client.start_transaction()
        assert tx_id is not None
        
        # Add data to transaction
        success = client.add_to_transaction(tx_id, """
            @prefix ex: <http://example.org/> .
            ex:test a ex:Test .
        """)
        assert success, "Failed to add data to transaction"
        
        # Commit transaction
        success = client.commit_transaction(tx_id)
        assert success, "Failed to commit transaction"
        
        # Verify data was added
        count = client.count_statements()
        assert count > 0, "Expected data to be added"

    def test_repository_inference(self, client):
        """Test repository inference settings."""
        # Enable inference
        settings = {
            "inference": True,
            "inferenceRules": [
                {
                    "name": "subClassOf",
                    "enabled": True
                }
            ]
        }
        success = client.set_repository_settings(settings)
        assert success, "Failed to enable inference"
        
        # Verify inference settings
        current_settings = client.get_repository_settings()
        assert current_settings["inference"] == True
        assert current_settings["inferenceRules"][0]["enabled"] == True

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

        # Test accessing non-existent repository
        response = requests.get(f"{base_url}/rest/repositories/non_existent_repo")
        assert response.status_code == 404

        # Test invalid query
        response = requests.get(
            f"{base_url}/repositories/test_repo",
            params={"query": "INVALID SPARQL QUERY"},
            headers={"Accept": "application/sparql-results+json"}
        )
        assert response.status_code in [400, 500]

        # Test invalid data format
        response = requests.post(
            f"{base_url}/repositories/test_repo/statements",
            data="Invalid data",
            headers={"Content-Type": "text/turtle"}
        )
        assert response.status_code in [400, 500]

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

        def query_data(i: int):
            query = f"""
PREFIX ex: <http://example.org/test#>
ASK {{ ex:TestClass{i} a ex:Class }}
"""
            headers = {"Accept": "application/sparql-results+json"}
            return requests.get(
                f"{base_url}/repositories/{test_repository}",
                params={"query": query},
                headers=headers
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Upload data concurrently
            upload_futures = [executor.submit(upload_data, i) for i in range(5)]
            for future in concurrent.futures.as_completed(upload_futures):
                response = future.result()
                assert response.status_code == 204

            # Query data concurrently
            query_futures = [executor.submit(query_data, i) for i in range(5)]
            for future in concurrent.futures.as_completed(query_futures):
                response = future.result()
                assert response.status_code == 200
                results = response.json()
                assert results["boolean"] is True

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

        # Verify all data was uploaded
        query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT (COUNT(*) as ?count) WHERE { ?s a ?o }
"""
        headers = {"Accept": "application/sparql-results+json"}
        response = requests.get(
            f"{base_url}/repositories/{test_repository}",
            params={"query": query},
            headers=headers
        )
        assert response.status_code == 200
        results = response.json()
        assert int(results["results"]["bindings"][0]["count"]["value"]) >= 1000

    def test_repository_size(self, base_url: str, test_repository: str):
        """Test getting repository size."""
        response = requests.get(f"{base_url}/repositories/{test_repository}/size")
        assert response.status_code == 200
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

        # Verify namespace was added
        response = requests.get(
            f"{base_url}/repositories/{test_repository}/namespaces",
            headers={"Accept": "application/sparql-results+json"}
        )
        assert response.status_code == 200
        namespaces = response.json()
        assert any(ns["prefix"]["value"] == test_prefix and 
                  ns["namespace"]["value"] == test_namespace 
                  for ns in namespaces["results"]["bindings"])

        # Delete the namespace
        response = requests.delete(
            f"{base_url}/repositories/{test_repository}/namespaces/{test_prefix}"
        )
        assert response.status_code in [200, 204]

    def test_repository_statistics(self, base_url: str, test_repository: str):
        """Test repository statistics."""
        # Get repository statistics
        response = requests.get(
            f"{base_url}/repositories/{test_repository}/size"
        )
        assert response.status_code == 200
        size = int(response.text)
        assert size >= 0

        # Get statement count
        query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }
"""
        headers = {"Accept": "application/sparql-results+json"}
        response = requests.get(
            f"{base_url}/repositories/{test_repository}",
            params={"query": query},
            headers=headers
        )
        assert response.status_code == 200
        results = response.json()
        statement_count = int(results["results"]["bindings"][0]["count"]["value"])
        assert statement_count >= 0