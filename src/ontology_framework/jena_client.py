"""
Module for interacting with GraphDB.
"""

import requests
from typing import Dict, List, Optional, Any, Union
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL
import os
import logging

class GraphDBError(Exception):
    """Base exception for GraphDB errors."""
    pass

class GraphDBClient:
    """Client for interacting with GraphDB."""
    
    def __init__(self, base_url: str = "http://localhost:7200", dataset: Optional[str] = None):
        """Initialize the client.
        
        Args:
            base_url: Base URL of the GraphDB server
            dataset: Optional default dataset name
        """
        self.base_url = base_url.rstrip('/')
        self.dataset = dataset
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
    def query(self, query: str, dataset: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute a SPARQL query.
        
        Args:
            query: The SPARQL query to execute
            dataset: Optional dataset name (uses default if not specified)
            
        Returns:
            List of query results as dictionaries
            
        Raises:
            GraphDBError: If query execution fails
        """
        try:
            dataset = dataset or self.dataset
            if not dataset:
                raise GraphDBError("No dataset specified")
                
            response = self.session.post(
                f"{self.base_url}/repositories/{dataset}",
                headers={'Accept': 'application/sparql-results+json'},
                params={'query': query}
            )
            response.raise_for_status()
            
            results = response.json()
            bindings = results['results']['bindings']
            
            return [
                {
                    var: binding[var]['value']
                    for var in binding
                }
                for binding in bindings
            ]
        except requests.RequestException as e:
            self.logger.error(f"Failed to execute query: {str(e)}")
            raise GraphDBError(f"Failed to execute query: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error executing query: {str(e)}")
            raise GraphDBError(f"Unexpected error executing query: {str(e)}")
            
    def update(self, update: str, dataset: Optional[str] = None) -> bool:
        """Execute a SPARQL update.
        
        Args:
            update: The SPARQL update to execute
            dataset: Optional dataset name (uses default if not specified)
            
        Returns:
            True if update was successful
            
        Raises:
            GraphDBError: If update execution fails
        """
        try:
            dataset = dataset or self.dataset
            if not dataset:
                raise GraphDBError("No dataset specified")
                
            response = self.session.post(
                f"{self.base_url}/repositories/{dataset}/statements",
                headers={'Content-Type': 'application/sparql-update'},
                data=update
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            self.logger.error(f"Failed to execute update: {str(e)}")
            raise GraphDBError(f"Failed to execute update: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error executing update: {str(e)}")
            raise GraphDBError(f"Unexpected error executing update: {str(e)}")
            
    def upload_graph(self, graph: Union[str, Graph], dataset: Optional[str] = None) -> bool:
        """Upload an RDF graph.
        
        Args:
            graph: RDF graph as string or rdflib.Graph
            dataset: Optional dataset name (uses default if not specified)
            
        Returns:
            True if upload was successful
            
        Raises:
            GraphDBError: If upload fails
        """
        try:
            dataset = dataset or self.dataset
            if not dataset:
                raise GraphDBError("No dataset specified")
                
            if isinstance(graph, str):
                data = graph
                content_type = 'text/turtle'
            else:
                data = graph.serialize(format='turtle')
                content_type = 'text/turtle'
                
            response = self.session.post(
                f"{self.base_url}/rest/repositories/{dataset}/statements",
                headers={'Content-Type': content_type},
                data=data
            )
            
            if response.status_code >= 400:
                raise GraphDBError(f"Failed to upload graph: {response.text}")
                
            return True
        except requests.RequestException as e:
            self.logger.error(f"Failed to upload graph: {str(e)}")
            raise GraphDBError(f"Failed to upload graph: {str(e)}")
        except GraphDBError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error uploading graph: {str(e)}")
            raise GraphDBError(f"Unexpected error uploading graph: {str(e)}")
            
    def download_graph(self, dataset: Optional[str] = None) -> Graph:
        """Download an RDF graph.
        
        Args:
            dataset: Optional dataset name (uses default if not specified)
            
        Returns:
            RDF graph as rdflib.Graph
            
        Raises:
            GraphDBError: If download fails
        """
        try:
            dataset = dataset or self.dataset
            if not dataset:
                raise GraphDBError("No dataset specified")
                
            response = self.session.get(
                f"{self.base_url}/rest/repositories/{dataset}/statements",
                headers={'Accept': 'text/turtle'}
            )
            response.raise_for_status()
            
            graph = Graph()
            graph.parse(data=response.text, format='turtle')
            return graph
        except requests.RequestException as e:
            self.logger.error(f"Failed to download graph: {str(e)}")
            raise GraphDBError(f"Failed to download graph: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error downloading graph: {str(e)}")
            raise GraphDBError(f"Unexpected error downloading graph: {str(e)}")
            
    def clear_graph(self, dataset: Optional[str] = None) -> bool:
        """Clear all triples from a graph.
        
        Args:
            dataset: Optional dataset name (uses default if not specified)
            
        Returns:
            True if clear was successful
            
        Raises:
            GraphDBError: If clear fails
        """
        try:
            dataset = dataset or self.dataset
            if not dataset:
                raise GraphDBError("No dataset specified")
                
            response = self.session.delete(
                f"{self.base_url}/rest/repositories/{dataset}/statements"
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            self.logger.error(f"Failed to clear graph: {str(e)}")
            raise GraphDBError(f"Failed to clear graph: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error clearing graph: {str(e)}")
            raise GraphDBError(f"Unexpected error clearing graph: {str(e)}")
            
    def list_graphs(self, dataset: Optional[str] = None) -> List[str]:
        """List available graphs in a dataset.
        
        Args:
            dataset: Optional dataset name (uses default if not specified)
            
        Returns:
            List of graph names
            
        Raises:
            GraphDBError: If listing fails
        """
        try:
            dataset = dataset or self.dataset
            if not dataset:
                raise GraphDBError("No dataset specified")
                
            response = self.session.get(
                f"{self.base_url}/rest/repositories/{dataset}/contexts"
            )
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to list graphs: {str(e)}")
            raise GraphDBError(f"Failed to list graphs: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error listing graphs: {str(e)}")
            raise GraphDBError(f"Unexpected error listing graphs: {str(e)}")
            
    def count_triples(self, dataset: Optional[str] = None) -> int:
        """Count triples in a dataset.
        
        Args:
            dataset: Optional dataset name (uses default if not specified)
            
        Returns:
            Number of triples
            
        Raises:
            GraphDBError: If counting fails
        """
        try:
            dataset = dataset or self.dataset
            if not dataset:
                raise GraphDBError("No dataset specified")
                
            response = self.session.get(
                f"{self.base_url}/rest/repositories/{dataset}/size"
            )
            response.raise_for_status()
            
            return int(response.text)
        except requests.RequestException as e:
            self.logger.error(f"Failed to count triples: {str(e)}")
            raise GraphDBError(f"Failed to count triples: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error counting triples: {str(e)}")
            raise GraphDBError(f"Unexpected error counting triples: {str(e)}")
            
    def get_graph_info(self, dataset: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a graph.
        
        Args:
            dataset: Optional dataset name (uses default if not specified)
            
        Returns:
            Dictionary containing graph information
            
        Raises:
            GraphDBError: If getting info fails
        """
        try:
            dataset = dataset or self.dataset
            if not dataset:
                raise GraphDBError("No dataset specified")
                
            response = self.session.get(
                f"{self.base_url}/rest/repositories/{dataset}"
            )
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to get graph info: {str(e)}")
            raise GraphDBError(f"Failed to get graph info: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error getting graph info: {str(e)}")
            raise GraphDBError(f"Unexpected error getting graph info: {str(e)}")
            
    def backup_graph(self, backup_path: str, dataset: Optional[str] = None) -> bool:
        """Backup a graph to a file.
        
        Args:
            backup_path: Path to save the backup
            dataset: Optional dataset name (uses default if not specified)
            
        Returns:
            True if backup was successful
            
        Raises:
            GraphDBError: If backup fails
        """
        try:
            dataset = dataset or self.dataset
            if not dataset:
                raise GraphDBError("No dataset specified")
                
            response = self.session.get(
                f"{self.base_url}/rest/repositories/{dataset}/statements",
                headers={'Accept': 'text/turtle'}
            )
            response.raise_for_status()
            
            with open(backup_path, 'w') as f:
                f.write(response.text)
            return True
        except requests.RequestException as e:
            raise GraphDBError(f"Failed to backup graph: {str(e)}")
        except Exception as e:
            raise GraphDBError(f"Unexpected error backing up graph: {str(e)}")
            
    def restore_graph(self, backup_path: str, dataset: Optional[str] = None) -> bool:
        """Restore a graph from a backup file.
        
        Args:
            backup_path: Path to the backup file
            dataset: Optional dataset name (uses default if not specified)
            
        Returns:
            True if restore was successful
            
        Raises:
            GraphDBError: If restore fails
        """
        try:
            dataset = dataset or self.dataset
            if not dataset:
                raise GraphDBError("No dataset specified")
                
            with open(backup_path, 'r') as f:
                data = f.read()
                
            response = self.session.post(
                f"{self.base_url}/rest/repositories/{dataset}/statements",
                headers={'Content-Type': 'text/turtle'},
                data=data
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            raise GraphDBError(f"Failed to restore graph: {str(e)}")
        except Exception as e:
            raise GraphDBError(f"Unexpected error restoring graph: {str(e)}")
            
    def load_ontology(self, dataset: str, ontology_path: str) -> bool:
        """Load an ontology into a dataset.
        
        Args:
            dataset: Name of the dataset
            ontology_path: Path to the ontology file
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            GraphDBError: If loading fails
        """
        if not os.path.exists(ontology_path):
            raise GraphDBError(f"Ontology file not found: {ontology_path}")
            
        try:
            # Clear existing data
            self.clear_graph(dataset)
            
            # Upload the ontology
            with open(ontology_path, 'rb') as f:
                response = self.session.post(
                    f"{self.base_url}/rest/repositories/{dataset}/statements",
                    headers={"Content-Type": "application/rdf+xml"},
                    data=f.read()
                )
                
            response.raise_for_status()
            return True
            
        except requests.RequestException as e:
            raise GraphDBError(f"Failed to load ontology: {str(e)}")
        except Exception as e:
            raise GraphDBError(f"Error loading ontology: {str(e)}") 