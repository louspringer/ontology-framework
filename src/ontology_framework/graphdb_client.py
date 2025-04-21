"""GraphDB client for interacting with a GraphDB server.

This module provides a client for interacting with a GraphDB server, supporting operations
such as repository creation, data import, and SPARQL query execution.
"""

import logging
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

class GraphDBError(Exception):
    """Exception raised for GraphDB-related errors."""
    pass

class GraphDBClient:
    """Client for interacting with a GraphDB server."""
    
    def __init__(
        self,
        endpoint: str,
        repository: str,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:
        """Initialize the GraphDB client.
        
        Args:
            endpoint: The GraphDB server endpoint URL.
            repository: The name of the repository to work with.
            username: Optional username for authentication.
            password: Optional password for authentication.
        """
        self.endpoint = endpoint.rstrip("/")
        self.repository = repository
        self.auth = HTTPBasicAuth(username, password) if username and password else None
        self.logger = logging.getLogger(__name__)
    
    def create_repository(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Create a new repository.
        
        Args:
            config: Optional repository configuration.
            
        Raises:
            GraphDBError: If repository creation fails.
        """
        url = f"{self.endpoint}/rest/repositories"
        default_config = {
            "id": self.repository,
            "title": self.repository,
            "type": "free"
        }
        data = json.dumps(config or default_config)
        
        try:
            response = requests.post(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                auth=self.auth
            )
            response.raise_for_status()
            self.logger.info(f"Repository '{self.repository}' created successfully")
        except requests.exceptions.RequestException as e:
            raise GraphDBError(f"Failed to create repository: {str(e)}") from e
    
    def import_data(self, file_path: Union[str, Path]) -> None:
        """Import RDF data from a file.
        
        Args:
            file_path: Path to the file containing RDF data.
            
        Raises:
            GraphDBError: If data import fails.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise GraphDBError(f"File not found: {file_path}")
            
        url = f"{self.endpoint}/repositories/{self.repository}/statements"
        
        try:
            with open(file_path, "rb") as f:
                headers = {
                    'Content-Type': 'text/turtle',
                    'Content-Disposition': f'attachment; filename="{file_path}"'
                }
                response = requests.post(
                    url,
                    data=f,
                    headers=headers,
                    auth=self.auth
                )
                response.raise_for_status()
            self.logger.info(f"Data imported from {file_path}")
        except (requests.exceptions.RequestException, IOError) as e:
            raise GraphDBError(f"Failed to import data: {str(e)}") from e
    
    def query(self, sparql_query: str) -> Dict[str, Any]:
        """Execute a SPARQL query.
        
        Args:
            sparql_query: The SPARQL query to execute.
            
        Returns:
            The query results in JSON format.
            
        Raises:
            GraphDBError: If query execution fails.
        """
        url = f"{self.endpoint}/repositories/{self.repository}"
        params = {"query": sparql_query}
        
        try:
            start_time = time.time()
            response = requests.get(
                url,
                params=params,
                headers={"Accept": "application/sparql-results+json"},
                auth=self.auth
            )
            response.raise_for_status()
            
            duration = time.time() - start_time
            if duration > 1.0:  # Consider queries taking more than 1 second as slow
                self.logger.warning(f"Slow query detected (took {duration:.2f}s)")
            
            self.logger.info("Query executed")
            return response.json()
        except requests.exceptions.RequestException as e:
            raise GraphDBError(f"Failed to execute query: {str(e)}") from e