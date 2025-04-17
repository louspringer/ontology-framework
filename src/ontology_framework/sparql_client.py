#!/usr/bin/env python3
"""SPARQL client for ontology operations."""

import logging
import os
import requests
import time
import json
from typing import Dict, List, Optional, Union, Any, Tuple
from urllib.parse import urljoin
from rdflib import Graph, Dataset, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define namespaces
NS1 = Namespace("http://example.org/guidance#")

class SparqlClientError(Exception):
    """Base exception for SPARQL client errors."""
    pass

class AuthenticationError(SparqlClientError):
    """Authentication related errors."""
    pass

class DatasetError(SparqlClientError):
    """Dataset related errors."""
    pass

class QueryError(SparqlClientError):
    """Query related errors."""
    pass

class SparqlClient:
    """Client for interacting with Apache Jena Fuseki SPARQL server."""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    STARTUP_TIMEOUT = 30  # seconds
    
    # Content type constants
    TURTLE_CONTENT_TYPES = [
        'text/turtle',
        'application/x-turtle',
        'application/turtle'
    ]
    SPARQL_CONTENT_TYPES = [
        'application/sparql-query',
        'application/x-www-form-urlencoded'
    ]
    
    def __init__(self, base_url: str = "http://localhost:3030", auth: Optional[Tuple[str, str]] = None):
        """Initialize the SPARQL client.
        
        Args:
            base_url: Base URL of the Fuseki server
            auth: Optional tuple of (username, password) for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.dataset_name = "guidance"
        self.dataset_url = f"{self.base_url}/{self.dataset_name}"
        self.auth = auth
        self.session = requests.Session()
        if auth:
            self.session.auth = auth
        self.graph = Dataset()  # Use Dataset for named graph support
        
        # Wait for server to be available
        self._wait_for_server()
            
    def _wait_for_server(self) -> None:
        """Wait for the Fuseki server to be available.
        
        Raises:
            SparqlClientError: If server is not available after timeout
        """
        start_time = time.time()
        while time.time() - start_time < self.STARTUP_TIMEOUT:
            try:
                response = self.session.get(f"{self.base_url}/$/ping")
                if response.status_code == 200:
                    logger.info("Connected to Fuseki server")
                    return
            except requests.exceptions.RequestException:
                time.sleep(1)
        raise SparqlClientError(f"Fuseki server not available after {self.STARTUP_TIMEOUT} seconds")
            
    def _make_request(self, method: str, url: str, retry_count: int = 0, **kwargs) -> requests.Response:
        """Make an HTTP request with error handling and retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            retry_count: Current retry attempt
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            AuthenticationError: If authentication fails
            DatasetError: If dataset operation fails
            QueryError: If query operation fails
        """
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError(f"Authentication failed: {e}")
            elif e.response.status_code == 404:
                raise DatasetError(f"Dataset not found: {e}")
            elif e.response.status_code == 400:
                raise QueryError(f"Invalid query: {e}")
            elif e.response.status_code == 409:
                if "datasets" in url:
                    # Dataset already exists is not an error
                    logger.info(f"Dataset already exists: {url}")
                    return e.response
                raise DatasetError(f"Resource conflict: {e}")
            elif retry_count < self.MAX_RETRIES:
                logger.warning(f"Request failed, retrying ({retry_count + 1}/{self.MAX_RETRIES})")
                time.sleep(self.RETRY_DELAY)
                return self._make_request(method, url, retry_count + 1, **kwargs)
            else:
                raise SparqlClientError(f"HTTP error occurred after {self.MAX_RETRIES} retries: {e}")
        except requests.exceptions.RequestException as e:
            if retry_count < self.MAX_RETRIES:
                logger.warning(f"Request failed, retrying ({retry_count + 1}/{self.MAX_RETRIES})")
                time.sleep(self.RETRY_DELAY)
                return self._make_request(method, url, retry_count + 1, **kwargs)
            raise SparqlClientError(f"Request failed after {self.MAX_RETRIES} retries: {e}")
            
    def dataset_exists(self, dataset_name: Optional[str] = None) -> bool:
        """Check if a dataset exists.
        
        Args:
            dataset_name: Optional name of the dataset to check. If None, uses default.
            
        Returns:
            bool: True if dataset exists
        """
        try:
            name = dataset_name or self.dataset_name
            self._make_request('GET', f"{self.base_url}/$/datasets/{name}")
            return True
        except DatasetError:
            return False
        
    def create_dataset(self, dataset_name: Optional[str] = None) -> bool:
        """Create a new dataset in Fuseki.
        
        Args:
            dataset_name: Optional name for the dataset. If None, uses default.
            
        Returns:
            bool: True if dataset was created successfully
            
        Raises:
            AuthenticationError: If authentication fails
            DatasetError: If dataset creation fails
        """
        try:
            name = dataset_name or self.dataset_name
            
            # Check if dataset already exists
            if self.dataset_exists(name):
                logger.info(f"Dataset {name} already exists")
                return True
                
            self._make_request(
                'POST',
                f"{self.base_url}/$/datasets",
                json={
                    "dbName": name,
                    "dbType": "tdb2"
                },
                headers={'Content-Type': 'application/json'}
            )
            logger.info(f"Created dataset: {name}")
            return True
        except SparqlClientError as e:
            logger.error(f"Failed to create dataset: {e}")
            return False
            
    def delete_dataset(self, dataset_name: Optional[str] = None) -> bool:
        """Delete the dataset from Fuseki.
        
        Args:
            dataset_name: Optional name of dataset to delete. If None, uses default.
            
        Returns:
            bool: True if dataset was deleted successfully
            
        Raises:
            AuthenticationError: If authentication fails
            DatasetError: If dataset deletion fails
        """
        try:
            name = dataset_name or self.dataset_name
            if not self.dataset_exists(name):
                logger.info(f"Dataset {name} does not exist")
                return True
            self._make_request('DELETE', f"{self.base_url}/$/datasets/{name}")
            logger.info(f"Deleted dataset: {name}")
            return True
        except SparqlClientError as e:
            logger.error(f"Failed to delete dataset: {e}")
            return False
            
    def load_ontology(self, file_path: str, graph_name: Optional[str] = None) -> bool:
        """Load an ontology file into the graph.
        
        Args:
            file_path: Path to the ontology file
            graph_name: Optional name for the graph. If None, uses default graph.
            
        Returns:
            bool: True if ontology was loaded successfully
        """
        try:
            # Parse the file into a temporary graph
            temp_graph = Graph()
            temp_graph.parse(file_path, format='turtle')
            
            # Serialize the graph
            turtle_data = temp_graph.serialize(format='turtle')
            
            # If graph_name is specified, use the graph parameter
            params = {}
            if graph_name:
                params['graph'] = graph_name
            
            # Try different content types until one works
            for content_type in self.TURTLE_CONTENT_TYPES:
                try:
                    self._make_request(
                        'POST',
                        f"{self.dataset_url}/data",
                        data=turtle_data,
                        params=params,
                        headers={
                            'Content-Type': f'{content_type}; charset=utf-8',
                            'Accept': ','.join(self.TURTLE_CONTENT_TYPES)
                        }
                    )
                logger.info(f"Loaded ontology from: {file_path}")
                return True
                except QueryError:
                    continue
            
            raise QueryError("Failed to load ontology with any supported content type")
        except (SparqlClientError, IOError) as e:
            logger.error(f"Failed to load ontology: {e}")
            return False
            
    def execute_query(self, query: str, graph_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute a SPARQL query against the graph.
        
        Args:
            query: SPARQL query string
            graph_name: Optional name of graph to query. If None, uses default graph.
            
        Returns:
            List of query results as dictionaries
            
        Raises:
            AuthenticationError: If authentication fails
            DatasetError: If dataset not found
            QueryError: If query is invalid
        """
        try:
            # Add prefixes for common namespaces
            prefixes = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX meta: <http://example.org/guidance/meta#>
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            """
            
            # If graph_name is specified and query doesn't already have a GRAPH clause
            if graph_name and 'GRAPH' not in query.upper():
                # Handle both SELECT and CONSTRUCT queries
                if query.strip().upper().startswith('SELECT'):
                    # Extract the WHERE clause
                    parts = query.split('WHERE', 1)
                    if len(parts) == 2:
                        select_clause = parts[0]
                        where_clause = parts[1]
                        query = f"{prefixes}\n{select_clause} WHERE {{ GRAPH <{graph_name}> {where_clause} }}"
                    else:
                        query = f"{prefixes}\n{query}"
                else:
                    query = f"{prefixes}\nWITH <{graph_name}>\n{query}"
            else:
                query = f"{prefixes}\n{query}"
            
            # Try different content types until one works
            for content_type in self.SPARQL_CONTENT_TYPES:
                try:
                    if content_type == 'application/x-www-form-urlencoded':
                        response = self._make_request(
                            'POST',
                            f"{self.dataset_url}/sparql",
                data={'query': query},
                            headers={
                                'Accept': 'application/sparql-results+json'
                            }
                        )
                    else:
                        response = self._make_request(
                            'POST',
                            f"{self.dataset_url}/sparql",
                            data=query,
                            headers={
                                'Content-Type': f'{content_type}; charset=utf-8',
                                'Accept': 'application/sparql-results+json'
                            }
                        )
                    
                    try:
            results = response.json()
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode JSON response: {e}")
                        continue
                        
            return results.get('results', {}).get('bindings', [])
                except QueryError:
                    continue
            
            raise QueryError("Failed to execute query with any supported content type")
        except SparqlClientError as e:
            logger.error(f"Failed to execute query: {e}")
            return []
            
    def validate_ontology(self, graph_name: Optional[str] = None, validation_query: Optional[str] = None) -> List[str]:
        """Validate the ontology using SHACL rules.
        
        Args:
            graph_name: Optional name of graph to validate. If None, uses default graph.
            validation_query: Optional custom validation query. If None, uses default SHACL validation.
            
        Returns:
            List of validation errors
            
        Raises:
            AuthenticationError: If authentication fails
            DatasetError: If dataset not found
            QueryError: If validation query is invalid
        """
        if validation_query:
            try:
                results = self.execute_query(validation_query, graph_name)
                return [str(result) for result in results]
            except SparqlClientError as e:
                logger.error(f"Failed to validate ontology: {e}")
                return [f"Validation error: {str(e)}"]
                
        # Default SHACL validation
        query = """
        SELECT ?shape ?path ?minCount ?maxCount ?datatype ?message
        WHERE {
            ?shape a sh:NodeShape .
            ?shape sh:property ?property .
            ?property sh:path ?path .
            OPTIONAL { ?property sh:minCount ?minCount }
            OPTIONAL { ?property sh:maxCount ?maxCount }
            OPTIONAL { ?property sh:datatype ?datatype }
            OPTIONAL { ?property sh:message ?message }
        }
        """
        
        try:
            results = self.execute_query(query, graph_name)
            validation_errors = []
            
            for result in results:
                shape = result.get('shape', {}).get('value', '')
                path = result.get('path', {}).get('value', '')
                message = result.get('message', {}).get('value', '')
                
                if message:
                    validation_errors.append(f"{shape}: {message} (path: {path})")
                else:
                    validation_errors.append(f"{shape}: Validation failed for {path}")
                    
            return validation_errors
        except SparqlClientError as e:
            logger.error(f"Failed to validate ontology: {e}")
            return [f"Validation error: {str(e)}"] 
            return [f"Validation error: {str(e)}"] 
            return [f"Validation error: {str(e)}"] 
            return [f"Validation error: {str(e)}"] 
            return [f"Validation error: {str(e)}"] 
            return [f"Validation error: {str(e)}"] 