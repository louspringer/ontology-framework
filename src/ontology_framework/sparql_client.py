from requests import Session
from requests.exceptions import RequestException
from typing import Dict, List, Any, Optional
from .exceptions import SparqlClientError
import warnings
import os

class SparqlClient:
    """Client for interacting with SPARQL endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:7200", server_type: str = "graphdb"):
        """Initialize the SPARQL client.
        
        Args:
            base_url: Base URL of the SPARQL server (default: GraphDB)
            server_type: Type of server (default: "graphdb")
            
        Note:
            Fuseki support is deprecated. Use GraphDB instead.
        """
        if server_type != "graphdb":
            warnings.warn(
                "Fuseki support is deprecated. Use GraphDB instead.",
                DeprecationWarning,
                stacklevel=2
            )
        self.base_url = base_url
        self.server_type = server_type
        self.session = Session()

    def dataset_exists(self, dataset: str) -> bool:
        """Check if a dataset exists.
        
        Args:
            dataset: Name of the dataset to check
            
        Returns:
            True if dataset exists, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/rest/repositories/{dataset}")
            return response.status_code == 200
        except RequestException:
            return False

    def create_dataset(self, dataset: str) -> bool:
        """Create a new dataset.
        
        Args:
            dataset: Name of the dataset
            
        Returns:
            True if dataset was created successfully
            
        Raises:
            SparqlClientError: If dataset creation fails
        """
        try:
            # Check if dataset already exists
            if self.dataset_exists(dataset):
                return True
                
            if self.server_type == "graphdb":
                # First create the repository configuration
                config_response = self.session.post(
                    f"{self.base_url}/rest/repositories",
                    headers={"Content-Type": "application/json"},
                    json={
                        "id": dataset,
                        "title": dataset,
                        "type": "graphdb:FreeSailRepository",
                        "params": {
                            "ruleset": "rdfsplus-optimized",
                            "query-timeout": 0,
                            "query-limit-results": 0,
                            "check-for-inconsistencies": False,
                            "disable-sameAs": True,
                            "enable-context-index": True,
                            "enablePredicateList": True,
                            "enable-fts-index": True,
                            "fts-indexes": [
                                {
                                    "predicates": [
                                        "http://www.w3.org/2000/01/rdf-schema#label",
                                        "http://www.w3.org/2004/02/skos/core#prefLabel",
                                        "http://www.w3.org/2004/02/skos/core#altLabel"
                                    ],
                                    "minWordLength": 3,
                                    "stopWords": [],
                                    "caseSensitive": False,
                                    "language": "en"
                                }
                            ]
                        }
                    }
                )
                config_response.raise_for_status()
                
                # Then initialize the repository
                init_response = self.session.post(
                    f"{self.base_url}/rest/repositories/{dataset}/init",
                    headers={"Content-Type": "application/json"}
                )
                init_response.raise_for_status()
                
                return True
            else:  # fuseki
                warnings.warn(
                    "Fuseki support is deprecated. Use GraphDB instead.",
                    DeprecationWarning,
                    stacklevel=2
                )
                response = self.session.post(
                    f"{self.base_url}/$$/datasets",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "dbName": dataset,
                        "dbType": "tdb2",
                        "ds.name": dataset
                    }
                )
                
            if response.status_code == 405:  # Method not allowed
                raise SparqlClientError(f"Server does not support dataset creation via API. Status: {response.status_code}")
                
            response.raise_for_status()
            return True
        except RequestException as e:
            raise SparqlClientError(f"Failed to create dataset: {str(e)}")
        except Exception as e:
            raise SparqlClientError(f"Unexpected error creating dataset: {str(e)}")

    def delete_dataset(self, dataset: str) -> bool:
        """Delete a dataset.
        
        Args:
            dataset: Name of the dataset to delete
            
        Returns:
            True if dataset was deleted successfully
            
        Raises:
            SparqlClientError: If dataset deletion fails
        """
        try:
            response = self.session.delete(f"{self.base_url}/rest/repositories/{dataset}")
            response.raise_for_status()
            return True
        except RequestException as e:
            raise SparqlClientError(f"Failed to delete dataset: {str(e)}")
        except Exception as e:
            raise SparqlClientError(f"Unexpected error deleting dataset: {str(e)}")

    def execute_query(self, query: str, dataset: str) -> List[Dict[str, Any]]:
        """Execute a SPARQL query.
        
        Args:
            query: The SPARQL query to execute
            dataset: Name of the dataset to query
            
        Returns:
            List of query results as dictionaries
            
        Raises:
            SparqlClientError: If query execution fails
        """
        try:
            response = self.session.post(
                f"{self.base_url}/repositories/{dataset}",
                headers={'Accept': 'application/sparql-results+json'},
                params={'query': query}
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
        except RequestException as e:
            raise SparqlClientError(f"Failed to execute query: {str(e)}")
        except Exception as e:
            raise SparqlClientError(f"Unexpected error executing query: {str(e)}")

    def load_ontology(self, dataset: str, ontology_path: str) -> bool:
        """Load an ontology into a dataset.
        
        Args:
            dataset: Name of the dataset
            ontology_path: Path to the ontology file
            
        Returns:
            True if ontology was loaded successfully
            
        Raises:
            SparqlClientError: If ontology loading fails
        """
        try:
            if not os.path.exists(ontology_path):
                raise SparqlClientError(f"Ontology file not found: {ontology_path}")
                
            if self.server_type == "graphdb":
                # First clear any existing data
                self.clear_dataset(dataset)
                
                # Upload the ontology file
                with open(ontology_path, 'rb') as f:
                    response = self.session.post(
                        f"{self.base_url}/rest/repositories/{dataset}/statements",
                        headers={"Content-Type": "application/rdf+xml"},
                        data=f.read()
                    )
                response.raise_for_status()
                return True
            else:  # fuseki
                warnings.warn(
                    "Fuseki support is deprecated. Use GraphDB instead.",
                    DeprecationWarning,
                    stacklevel=2
                )
                with open(ontology_path, 'rb') as f:
                    response = self.session.post(
                        f"{self.base_url}/{dataset}/data",
                        headers={"Content-Type": "application/rdf+xml"},
                        data=f.read()
                    )
                response.raise_for_status()
                return True
        except RequestException as e:
            raise SparqlClientError(f"Failed to load ontology: {str(e)}")
        except Exception as e:
            raise SparqlClientError(f"Unexpected error loading ontology: {str(e)}")

    def validate_ontology(self, dataset: str) -> List[Dict[str, Any]]:
        """Validate an ontology in a dataset.
        
        Args:
            dataset: Name of the dataset to validate
            
        Returns:
            List of validation results
            
        Raises:
            SparqlClientError: If validation fails
        """
        try:
            # Query for validation rules
            query = """
            PREFIX sh: <http://www.w3.org/ns/shacl#>
            SELECT ?shape ?targetClass ?property ?minCount ?maxCount ?datatype
            WHERE {
                ?shape a sh:NodeShape .
                OPTIONAL { ?shape sh:targetClass ?targetClass }
                OPTIONAL {
                    ?shape sh:property ?propertyNode .
                    ?propertyNode sh:path ?property .
                    OPTIONAL { ?propertyNode sh:minCount ?minCount }
                    OPTIONAL { ?propertyNode sh:maxCount ?maxCount }
                    OPTIONAL { ?propertyNode sh:datatype ?datatype }
                }
            }
            """
            return self.execute_query(query, dataset)
        except Exception as e:
            raise SparqlClientError(f"Failed to validate ontology: {str(e)}")