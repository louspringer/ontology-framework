"""
Module for interacting with Apache Jena Fuseki.
"""

import requests
from typing import Dict, List, Optional, Any
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL

class JenaError(Exception):
    """Base exception for Jena client errors."""
    pass

class JenaConnectionError(JenaError):
    """Exception raised when connection to Jena fails."""
    pass

class JenaQueryError(JenaError):
    """Exception raised when a SPARQL query fails."""
    pass

class JenaUpdateError(JenaError):
    """Exception raised when a SPARQL update fails."""
    pass

class JenaFusekiClient:
    """Client for interacting with Apache Jena Fuseki."""
    
    def __init__(self, endpoint_url: str, dataset: str):
        """Initialize the client.
        
        Args:
            endpoint_url: Base URL of the Fuseki server
            dataset: Name of the dataset to work with
        """
        self.endpoint_url = endpoint_url.rstrip('/')
        self.dataset = dataset
        self.query_url = f"{self.endpoint_url}/{dataset}/query"
        self.update_url = f"{self.endpoint_url}/{dataset}/update"
        self.graph_store_url = f"{self.endpoint_url}/{dataset}/data"
        
    def query(self, sparql_query: str) -> List[Dict[str, Any]]:
        """Execute a SPARQL query.
        
        Args:
            sparql_query: The SPARQL query to execute
            
        Returns:
            List of query results as dictionaries
            
        Raises:
            JenaConnectionError: If connection fails
            JenaQueryError: If query execution fails
        """
        try:
            response = requests.post(
                self.query_url,
                headers={'Accept': 'application/sparql-results+json'},
                params={'query': sparql_query}
            )
            response.raise_for_status()
            
            results = response.json()
            bindings = results['results']['bindings']
            
            # Convert results to a more usable format
            return [
                {
                    var: binding[var]['value']
                    for var in binding
                }
                for binding in bindings
            ]
            
        except requests.ConnectionError as e:
            raise JenaConnectionError(f"Failed to connect to Jena: {str(e)}")
        except requests.HTTPError as e:
            raise JenaQueryError(f"Query failed: {str(e)}")
        except Exception as e:
            raise JenaError(f"Unexpected error: {str(e)}")
            
    def update(self, sparql_update: str) -> None:
        """Execute a SPARQL update.
        
        Args:
            sparql_update: The SPARQL update to execute
            
        Raises:
            JenaConnectionError: If connection fails
            JenaUpdateError: If update execution fails
        """
        try:
            response = requests.post(
                self.update_url,
                headers={'Content-Type': 'application/sparql-update'},
                data=sparql_update
            )
            response.raise_for_status()
            
        except requests.ConnectionError as e:
            raise JenaConnectionError(f"Failed to connect to Jena: {str(e)}")
        except requests.HTTPError as e:
            raise JenaUpdateError(f"Update failed: {str(e)}")
        except Exception as e:
            raise JenaError(f"Unexpected error: {str(e)}")
            
    def upload_graph(self, graph: Graph, graph_uri: Optional[str] = None) -> None:
        """Upload an RDF graph.
        
        Args:
            graph: The RDF graph to upload
            graph_uri: Optional URI for the named graph
            
        Raises:
            JenaConnectionError: If connection fails
            JenaError: If upload fails
        """
        try:
            # Serialize the graph to Turtle format
            data = graph.serialize(format='turtle')
            
            headers = {'Content-Type': 'text/turtle'}
            params = {}
            if graph_uri:
                params['graph'] = graph_uri
                
            response = requests.post(
                self.graph_store_url,
                headers=headers,
                params=params,
                data=data
            )
            response.raise_for_status()
            
        except requests.ConnectionError as e:
            raise JenaConnectionError(f"Failed to connect to Jena: {str(e)}")
        except Exception as e:
            raise JenaError(f"Failed to upload graph: {str(e)}")
            
    def download_graph(self, graph_uri: Optional[str] = None) -> Graph:
        """Download an RDF graph.
        
        Args:
            graph_uri: Optional URI of the named graph to download
            
        Returns:
            The downloaded RDF graph
            
        Raises:
            JenaConnectionError: If connection fails
            JenaError: If download fails
        """
        try:
            params = {}
            if graph_uri:
                params['graph'] = graph_uri
                
            response = requests.get(
                self.graph_store_url,
                headers={'Accept': 'text/turtle'},
                params=params
            )
            response.raise_for_status()
            
            # Parse the response into a new graph
            graph = Graph()
            graph.parse(data=response.text, format='turtle')
            return graph
            
        except requests.ConnectionError as e:
            raise JenaConnectionError(f"Failed to connect to Jena: {str(e)}")
        except Exception as e:
            raise JenaError(f"Failed to download graph: {str(e)}")
            
    def clear_graph(self, graph_uri: Optional[str] = None) -> None:
        """Clear all triples from a graph.
        
        Args:
            graph_uri: Optional URI of the named graph to clear
            
        Raises:
            JenaConnectionError: If connection fails
            JenaUpdateError: If clear operation fails
        """
        if graph_uri:
            update = f"CLEAR GRAPH <{graph_uri}>"
        else:
            update = "CLEAR DEFAULT"
            
        self.update(update)
        
    def list_graphs(self) -> List[str]:
        """List all named graphs in the dataset.
        
        Returns:
            List of graph URIs
            
        Raises:
            JenaConnectionError: If connection fails
            JenaQueryError: If query fails
        """
        query = """
        SELECT DISTINCT ?g
        WHERE {
            GRAPH ?g { ?s ?p ?o }
        }
        """
        
        results = self.query(query)
        return [result['g'] for result in results]
        
    def count_triples(self, graph_uri: Optional[str] = None) -> int:
        """Count triples in a graph.
        
        Args:
            graph_uri: Optional URI of the named graph to count
            
        Returns:
            Number of triples
            
        Raises:
            JenaConnectionError: If connection fails
            JenaQueryError: If query fails
        """
        if graph_uri:
            query = f"""
            SELECT (COUNT(*) as ?count)
            WHERE {{
                GRAPH <{graph_uri}> {{ ?s ?p ?o }}
            }}
            """
        else:
            query = """
            SELECT (COUNT(*) as ?count)
            WHERE {
                ?s ?p ?o
            }
            """
            
        results = self.query(query)
        return int(results[0]['count']) 