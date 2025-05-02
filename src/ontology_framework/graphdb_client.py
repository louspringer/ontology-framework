"""GraphDB client for interacting with a GraphDB server.

This module provides a client for interacting with a GraphDB server, supporting operations
such as repository creation, data import, and SPARQL query execution.

Example:
    >>> client = GraphDBClient()
    >>> client.check_server_status()
    True
    >>> client.query("SELECT * WHERE { ?s ?p ?o }")
    [{'s': '...', 'p': '...', 'o': '...'}]
"""

import logging
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, TypedDict, cast

import requests
from requests.auth import HTTPBasicAuth
from rdflib import Graph, URIRef, RDFS, RDF, Literal, BNode, Namespace
import tempfile
import os

# Define GraphDB-specific namespaces
REP = Namespace("http://www.openrdf.org/config/repository#")
SR = Namespace("http://www.openrdf.org/config/repository/sail#")
SAIL = Namespace("http://www.openrdf.org/config/sail#")
OWLIM = Namespace("http://www.ontotext.com/trree/owlim#")

logger = logging.getLogger(__name__)

class GraphDBError(Exception):
    """Base exception for GraphDB client errors."""
    pass

class QueryResult(TypedDict):
    """Type definition for SPARQL query results."""
    head: Dict[str, List[str]]
    results: Dict[str, List[Dict[str, Dict[str, str]]]]

class GraphDBClient:
    """Client for interacting with GraphDB.
    
    This client provides methods for interacting with a GraphDB server, including:
    - SPARQL query execution
    - Graph management (upload/download/clear)
    - Server status checking
    - Backup and restore operations
    
    Example:
        >>> client = GraphDBClient()
        >>> client.check_server_status()
        True
        >>> client.query("SELECT * WHERE { ?s ?p ?o }")
        [{'s': '...', 'p': '...', 'o': '...'}]
    """
    
    def __init__(self, base_url: str = "http://localhost:7200", repository: str = "test"):
        """Initialize the GraphDB client.
        
        Args:
            base_url: Base URL of the GraphDB server
            repository: Repository name
            
        Example:
            >>> client = GraphDBClient(base_url="http://localhost:7200", repository="myrepo")
        """
        self.base_url = base_url.rstrip('/')
        self.repository = repository
        self.logger = logging.getLogger(__name__)
        
    def _get_endpoint(self, path: str) -> str:
        """Get the full endpoint URL.
        
        Args:
            path: API path
            
        Returns:
            Full endpoint URL
            
        Example:
            >>> client._get_endpoint("/sparql")
            'http://localhost:7200/repositories/test/sparql'
        """
        return f"{self.base_url}/repositories/{self.repository}{path}"

    def check_server_status(self) -> bool:
        """Check if the GraphDB server is running.
        
        Returns:
            True if server is running, False otherwise
            
        Example:
            >>> client.check_server_status()
            True
            
        Raises:
            GraphDBError: If server check fails
        """
        try:
            response = requests.get(f"{self.base_url}/rest/repositories")
            return response.status_code == 200
        except requests.RequestException as e:
            raise GraphDBError(f"Server status check failed: {str(e)}")

    def query(self, query: str) -> Dict[str, Any]:
        """Execute a SPARQL query.
        
        Args:
            query: SPARQL query string
            
        Returns:
            Query results in JSON format
            
        Raises:
            GraphDBError: If query fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/repositories/{self.repository}",
                params={"query": query},
                headers={
                    "Accept": "application/sparql-results+json"
                }
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            raise GraphDBError(f"Query failed: {str(e)}")
        except Exception as e:
            raise GraphDBError(f"Unexpected error during query: {str(e)}")
            
    def update(self, update_query: str) -> bool:
        """Execute a SPARQL UPDATE query.
        
        Args:
            update_query: The SPARQL UPDATE query to execute
            
        Returns:
            True if successful
            
        Example:
            >>> update = '''
            ... INSERT DATA {
            ...     <http://example.org/s> <http://example.org/p> <http://example.org/o> .
            ... }
            ... '''
            >>> client.update(update)
            True
            
        Raises:
            GraphDBError: If update fails
        """
        try:
            # Send request to execute update
            response = requests.post(
                f"{self.base_url}/repositories/{self.repository}/statements",
                data=update_query,
                headers={"Content-Type": "application/sparql-update"}
            )
            
            response.raise_for_status()
            return True
            
        except requests.exceptions.HTTPError as e:
            raise GraphDBError(f"Update failed: {str(e)}")
        except Exception as e:
            raise GraphDBError(f"Unexpected error during update: {str(e)}")
            
    def upload_graph(self, graph: Graph, graph_uri: str | None = None) -> bool:
        """Upload an RDFlib Graph to the repository.
        
        Args:
            graph: The RDFlib Graph to upload
            graph_uri: Optional URI for the named graph to upload to
            
        Returns:
            True if successful
            
        Example:
            >>> g = Graph()
            >>> g.add((URIRef("http://example.org/s"), 
                      URIRef("http://example.org/p"), 
                      URIRef("http://example.org/o")))
            >>> client.upload_graph(g)
            True
            
        Raises:
            GraphDBError: If upload fails
        """
        try:
            # Serialize graph to N-Triples format
            data = graph.serialize(format="nt")
            
            # Set up request parameters
            params = {}
            if graph_uri:
                params["context"] = f"<{graph_uri}>"
                
            # Send request to upload data
            response = requests.post(
                f"{self.base_url}/repositories/{self.repository}/statements",
                data=data,
                params=params,
                headers={"Content-Type": "application/n-triples"}
            )
            
            response.raise_for_status()
            return True
            
        except requests.exceptions.HTTPError as e:
            raise GraphDBError(f"Upload failed: {str(e)}")
        except Exception as e:
            raise GraphDBError(f"Unexpected error during upload: {str(e)}")
            
    def download_graph(self, graph_uri: Optional[str] = None) -> Graph:
        """Download an RDF graph from GraphDB.
        
        Args:
            graph_uri: Optional graph URI
            
        Returns:
            RDF graph
        """
        try:
            params = {}
            if graph_uri:
                params["graph"] = graph_uri
                
            response = requests.get(
                self._get_endpoint("/rdf-graphs/service"),
                params=params,
                headers={"Accept": "text/turtle"}
            )
            response.raise_for_status()
            
            graph = Graph()
            graph.parse(data=response.text, format='turtle')
            return graph
        except Exception as e:
            raise GraphDBError(f"Download failed: {str(e)}")
            
    def clear_graph(self, graph_uri: Optional[str] = None) -> bool:
        """Clear a graph in GraphDB.
        
        Args:
            graph_uri: Optional graph URI
            
        Returns:
            True if successful
        """
        try:
            params = {}
            if graph_uri:
                params["graph"] = graph_uri
                
            response = requests.delete(
                self._get_endpoint("/rdf-graphs/service"),
                params=params
            )
            response.raise_for_status()
            return True
        except Exception as e:
            raise GraphDBError(f"Clear failed: {str(e)}")
            
    def list_graphs(self) -> List[str]:
        """List all graphs in the repository.
        
        Returns:
            List of graph URIs
        """
        try:
            response = requests.get(
                self._get_endpoint("/rdf-graphs"),
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            return [graph["graphName"] for graph in response.json()]
        except Exception as e:
            raise GraphDBError(f"List graphs failed: {str(e)}")
            
    def count_triples(self, graph_uri: Optional[str] = None) -> int:
        """Count triples in a graph.
        
        Args:
            graph_uri: Optional graph URI
            
        Returns:
            Number of triples
        """
        try:
            query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
            if graph_uri:
                query = f"SELECT (COUNT(*) as ?count) FROM <{graph_uri}> WHERE {{ ?s ?p ?o }}"
                
            result = cast(QueryResult, self.query(query))
            return int(result["results"]["bindings"][0]["count"]["value"])
        except Exception as e:
            raise GraphDBError(f"Count triples failed: {str(e)}")
            
    def get_graph_info(self, graph_uri: Optional[str] = None) -> Dict:
        """Get information about a graph.
        
        Args:
            graph_uri: Optional graph URI
            
        Returns:
            Graph information
        """
        try:
            info = {
                "triples": self.count_triples(graph_uri),
                "uri": graph_uri or "default"
            }
            return info
        except Exception as e:
            raise GraphDBError(f"Get graph info failed: {str(e)}")
            
    def backup_graph(self, backup_path: Union[str, Path]) -> bool:
        """Backup a graph to a file.
        
        Args:
            backup_path: Path to save backup
            
        Returns:
            True if successful
        """
        try:
            graph = self.download_graph()
            graph.serialize(destination=backup_path, format='turtle')
            return True
        except Exception as e:
            raise GraphDBError(f"Backup failed: {str(e)}")
            
    def restore_graph(self, backup_path: Union[str, Path]) -> bool:
        """Restore a graph from a backup file.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful
        """
        try:
            self.clear_graph()
            self.upload_graph(backup_path)
            return True
        except Exception as e:
            raise GraphDBError(f"Restore failed: {str(e)}")
            
    def load_ontology(self, ontology_path: Union[str, Path]) -> bool:
        """Load an ontology file into GraphDB.
        
        Args:
            ontology_path: Path to ontology file
            
        Returns:
            True if successful
        """
        try:
            return self.upload_graph(ontology_path)
        except Exception as e:
            raise GraphDBError(f"Load ontology failed: {str(e)}")

    def create_repository(self, repository_id: str, repository_title: str | None = None) -> bool:
        """Create a new repository in GraphDB.
        
        Args:
            repository_id: ID of the repository to create
            repository_title: Optional title for the repository
            
        Returns:
            True if successful
            
        Example:
            >>> client.create_repository("test", "Test Repository")
            True
            
        Raises:
            GraphDBError: If repository creation fails
        """
        try:
            # Create repository configuration using Turtle format
            config = f"""
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rep: <http://www.openrdf.org/config/repository#> .
@prefix sr: <http://www.openrdf.org/config/repository/sail#> .
@prefix sail: <http://www.openrdf.org/config/sail#> .
@prefix owlim: <http://www.ontotext.com/trree/owlim#> .

[] a rep:Repository ;
    rep:repositoryID "{repository_id}" ;
    rdfs:label "{repository_title or repository_id}" ;
    rep:repositoryImpl [
        rep:repositoryType "graphdb:SailRepository" ;
        sr:sailImpl [
            sail:sailType "graphdb:Sail" ;
            owlim:base-URL "http://example.org/{repository_id}#" ;
            owlim:defaultNS "http://example.org/{repository_id}#" ;
            owlim:entity-index-size "200000" ;
            owlim:entity-id-size "32" ;
            owlim:imports "" ;
            owlim:repository-type "file-repository" ;
            owlim:ruleset "owl-horst-optimized" ;
            owlim:storage-folder "storage" ;
            owlim:enable-context-index "true" ;
            owlim:enable-predicate-list "true" ;
            owlim:enable-literal-index "true" ;
            owlim:in-memory-literal-properties "true" ;
            owlim:enable-optimization "true" ;
            owlim:check-for-inconsistencies "false" ;
            owlim:disable-sameAs "true" ;
            owlim:query-timeout "0" ;
            owlim:query-limit-results "0" ;
            owlim:throw-QueryEvaluationException-on-timeout "false" ;
            owlim:read-only "false"
        ]
    ] .
"""
            # Create a temporary file with the configuration
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as f:
                f.write(config)
                config_file = f.name

            try:
                # Send request to create repository using multipart/form-data
                with open(config_file, 'rb') as f:
                    files = {'config': ('config.ttl', f, 'text/turtle')}
                    response = requests.post(
                        f"{self.base_url}/rest/repositories",
                        files=files,
                        headers={'Accept': 'application/json'}
                    )

                if response.status_code == 201:
                    return True
                else:
                    raise GraphDBError(f"Failed to create repository: {response.text}")

            finally:
                # Clean up temporary file
                os.unlink(config_file)

        except requests.exceptions.RequestException as e:
            raise GraphDBError(f"Error creating repository: {str(e)}")
        except Exception as e:
            raise GraphDBError(f"Unexpected error creating repository: {str(e)}")
        
    def delete_repository(self, repository_id: str) -> bool:
        """Delete a repository from GraphDB.
        
        Args:
            repository_id: ID of the repository to delete
            
        Returns:
            True if successful
            
        Example:
            >>> client.delete_repository("test")
            True
            
        Raises:
            GraphDBError: If repository deletion fails
        """
        try:
            response = requests.delete(f"{self.base_url}/rest/repositories/{repository_id}")
            
            if response.status_code >= 400:
                raise GraphDBError(f"Repository deletion failed: {response.text}")
                
            return True
        except Exception as e:
            raise GraphDBError(f"Repository deletion failed: {str(e)}")
        
    def list_repositories(self) -> List[Dict[str, Any]]:
        """List all repositories in GraphDB.
        
        Returns:
            List of repository information dictionaries
            
        Example:
            >>> client.list_repositories()
            [{'id': 'test', 'title': 'Test Repository', ...}]
            
        Raises:
            GraphDBError: If listing repositories fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/rest/repositories",
                headers={"Accept": "application/json"}
            )
            
            if response.status_code >= 400:
                raise GraphDBError(f"List repositories failed: {response.text}")
                
            return response.json()
        except Exception as e:
            raise GraphDBError(f"List repositories failed: {str(e)}")

    def set_repository_settings(self, settings: Dict[str, Any]) -> bool:
        """Set repository settings.
        
        Args:
            settings: Dictionary of settings to apply
            
        Returns:
            True if successful
            
        Example:
            >>> client.set_repository_settings({"readOnly": True})
            True
        """
        try:
            response = requests.post(
                f"{self.base_url}/rest/repositories/{self.repository}/settings",
                json=settings,
                headers={"Content-Type": "application/json"}
            )
            return response.status_code == 204
        except Exception as e:
            raise GraphDBError(f"Failed to set repository settings: {str(e)}")
            
    def get_repository_settings(self) -> Dict[str, Any]:
        """Get current repository settings.
        
        Returns:
            Dictionary of current settings
            
        Example:
            >>> client.get_repository_settings()
            {"readOnly": False, "inference": True}
        """
        try:
            response = requests.get(
                f"{self.base_url}/rest/repositories/{self.repository}/settings",
                headers={"Accept": "application/json"}
            )
            return response.json()
        except Exception as e:
            raise GraphDBError(f"Failed to get repository settings: {str(e)}")
            
    def start_transaction(self) -> str:
        """Start a new transaction.
        
        Returns:
            Transaction ID
            
        Example:
            >>> tx_id = client.start_transaction()
            >>> client.add_to_transaction(tx_id, "INSERT DATA { ... }")
        """
        try:
            response = requests.post(
                f"{self.base_url}/rest/repositories/{self.repository}/transactions"
            )
            if response.status_code == 201:
                return response.headers["Location"].split("/")[-1]
            raise GraphDBError("Failed to start transaction")
        except Exception as e:
            raise GraphDBError(f"Failed to start transaction: {str(e)}")
            
    def add_to_transaction(self, tx_id: str, data: str) -> bool:
        """Add data to a transaction.
        
        Args:
            tx_id: Transaction ID
            data: Data to add (SPARQL update or RDF data)
            
        Returns:
            True if successful
        """
        try:
            response = requests.post(
                f"{self.base_url}/rest/repositories/{self.repository}/transactions/{tx_id}/statements",
                data=data,
                headers={"Content-Type": "text/turtle"}
            )
            return response.status_code == 204
        except Exception as e:
            raise GraphDBError(f"Failed to add to transaction: {str(e)}")
            
    def commit_transaction(self, tx_id: str) -> bool:
        """Commit a transaction.
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            True if successful
        """
        try:
            response = requests.put(
                f"{self.base_url}/rest/repositories/{self.repository}/transactions/{tx_id}"
            )
            return response.status_code == 204
        except Exception as e:
            raise GraphDBError(f"Failed to commit transaction: {str(e)}")
            
    def rollback_transaction(self, tx_id: str) -> bool:
        """Rollback a transaction.
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            True if successful
        """
        try:
            response = requests.delete(
                f"{self.base_url}/rest/repositories/{self.repository}/transactions/{tx_id}"
            )
            return response.status_code == 204
        except Exception as e:
            raise GraphDBError(f"Failed to rollback transaction: {str(e)}")

    def upload_binary_rdf(self, data: bytes, graph_uri: str | None = None) -> bool:
        """Upload binary RDF data to the repository.
        
        Args:
            data: Binary RDF data to upload
            graph_uri: Optional URI for the named graph to upload to
            
        Returns:
            True if successful
            
        Raises:
            GraphDBError: If upload fails
        """
        try:
            # Set up request parameters
            params = {}
            if graph_uri:
                params["context"] = f"<{graph_uri}>"
                
            # Send request to upload binary data
            response = requests.post(
                f"{self.base_url}/repositories/{self.repository}/statements",
                data=data,
                params=params,
                headers={"Content-Type": "application/x-binary-rdf"}
            )
            
            response.raise_for_status()
            return True
            
        except requests.exceptions.HTTPError as e:
            raise GraphDBError(f"Binary RDF upload failed: {str(e)}")
        except Exception as e:
            raise GraphDBError(f"Unexpected error during binary RDF upload: {str(e)}")