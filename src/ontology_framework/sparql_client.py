"""
SPARQL client functionality for the ontology framework.

This module provides SPARQL query, update, and validation operations
with semantic compliance and ontology framework integration.
"""

# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: 1.0.0
# Behavioral-Profile: ClaudeReflector

from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from pyshacl import validate
from rdflib.term import Node
import requests
import json
import logging
import os # Added for environment variables
from requests.auth import HTTPBasicAuth # Added for authentication

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
SH = Namespace("http://www.w3.org/ns/shacl#")


class SPARQLClient:
    def __init__(self, base_url=None, repository=None, graph=None):
        self.base_url = base_url
        self.repository = repository
        # If base_url is provided, endpoint_url might be derived or not used directly in old way
        # For now, let's ensure endpoint_url is None if base_url is used, to avoid confusion
        # in existing methods until they are updated.
        self.endpoint_url = None # This client uses base_url and repository for remote operations
        
        self.graph = graph or Graph()

        # Setup authentication from environment variables
        username = os.environ.get("GRAPHDB_USERNAME")
        password = os.environ.get("GRAPHDB_PASSWORD")
        if username and password:
            self._auth = HTTPBasicAuth(username, password)
            logger.debug(f"SPARQLClient initialized with user: {username} for remote operations.")
        else:
            self._auth = None
            logger.debug("SPARQLClient initialized without authentication for remote operations (credentials not found in env).")
        
    def onto_load_ontology(self, ontology_path):
        """Load ontology into the graph"""
        self.graph.parse(ontology_path, format="turtle")
        logger.info(f"Loaded ontology from {ontology_path}")
        
    def sparql_query(self, sparql_query):
        """Execute SPARQL query"""
        if self.base_url and self.repository: # Remote mode
            query_endpoint = f"{self.base_url}/repositories/{self.repository}"
            try:
                response = requests.get(
                    query_endpoint,
                    params={'query': sparql_query},
                    headers={'Accept': 'application/sparql-results+json'},
                    auth=self._auth
                )
                response.raise_for_status()
                raw_json_results = response.json()
                
                # Process raw JSON to match local query result structure
                processed_results = []
                if 'results' in raw_json_results and 'bindings' in raw_json_results['results']:
                    for binding in raw_json_results['results']['bindings']:
                        row_dict = {}
                        for var_name, var_data in binding.items():
                            if var_data['type'] == 'literal':
                                row_dict[var_name] = var_data['value']
                            elif var_data['type'] == 'uri':
                                row_dict[var_name] = var_data['value'] # Keep as full URI string
                            elif var_data['type'] == 'bnode':
                                row_dict[var_name] = f"_:{var_data['value']}" # Standard BNode string rep
                            else:
                                row_dict[var_name] = var_data['value'] 
                        processed_results.append(row_dict)
                
                # Reconstruct a similar structure to what rdflib's query might give,
                # or simply return the list of processed bindings if that's what tests expect.
                # For now, let's return the processed list directly if the original was a SELECT.
                # If it was an ASK query, the structure is different.
                if 'boolean' in raw_json_results: # ASK query
                    return [{'ASK': raw_json_results['boolean']}]
                
                # For SELECT, wrap processed_results in the standard structure
                # This part might need adjustment based on how tests use it.
                # The local query returns a list of dicts directly.
                # Let's make remote also return a list of dicts for SELECT.
                # The test assertions expect a dict with "results" and "bindings" keys.
                # So, we should reconstruct that.
                final_results_obj = {
                    "head": raw_json_results.get("head", {}), # Preserve head if it exists
                    "results": {"bindings": processed_results}
                }
                return final_results_obj

            except requests.exceptions.RequestException as e:
                logger.error(f"Remote SPARQL query failed: {e}")
                raise # Or return an error structure
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON response from remote query: {e}. Response text: {response.text[:200]}")
                raise # Or return an error structure
        elif self.endpoint_url: # Old direct endpoint_url logic (for current mock compatibility if needed temporarily)
            # This branch will likely be removed once mock is updated.
            # For now, ensure it also uses auth if self.endpoint_url was somehow set directly.
            query_endpoint = f"{self.endpoint_url}/sparql" 
            response = requests.get( 
                query_endpoint,
                params={'query': sparql_query}, 
                headers={'Accept': 'application/sparql-results+json'},
                auth=self._auth
            )
            response.raise_for_status()
            return response.json()
        else: # Local mode
            results = []
            try:
                qres = self.graph.query(sparql_query)
                # Handle ASK queries (returns bool or result with askAnswer)
                if hasattr(qres, 'askAnswer'):
                    return [{'ASK': bool(qres.askAnswer)}]
                if isinstance(qres, bool):
                    return [{'ASK': qres}]
                if qres is None:
                    logger.error("SPARQL query returned None. Query: %s", sparql_query)
                    return []
                for row in qres:
                    result = {}
                    for var in qres.vars:
                        value = row[var]
                        if isinstance(value, URIRef):
                            result[var] = str(value)
                        elif isinstance(value, Literal):
                            result[var] = value.value
                        else:
                            result[var] = str(value)
                    results.append(result)
            except Exception as e:
                logger.error(f"SPARQL query failed: {e}\nQuery: {sparql_query}")
                return []
            return results
            
    def sparql_update(self, sparql_update):
        """Execute SPARQL update"""
        if self.base_url and self.repository: # Remote mode
            update_endpoint = f"{self.base_url}/repositories/{self.repository}/statements"
            try:
                response = requests.post(
                    update_endpoint,
                    data=sparql_update,
                    headers={'Content-Type': 'application/sparql-update'},
                    auth=self._auth
                )
                response.raise_for_status()
                if response.status_code == 204:
                    return {"status": "success", "message": "Update successful, no content returned."}
                return response.json() # If other success codes might return JSON
            except requests.exceptions.RequestException as e:
                logger.error(f"Remote SPARQL update failed: {e}")
                raise # Or return an error structure
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON response from remote update: {e}. Response text: {response.text[:200]}")
                # If it was a 200 but not JSON, still could be success
                if response.ok:
                    return {"status": "success", "message": f"Update returned status {response.status_code} with non-JSON body."}
                raise
        elif self.endpoint_url: # Old direct endpoint_url logic
            update_endpoint = f"{self.endpoint_url}/update" 
            response = requests.post(
                update_endpoint,
                data=sparql_update, # Send raw update string
                headers={'Content-Type': 'application/sparql-update'},
                auth=self._auth
            )
            response.raise_for_status() # Raise an exception for HTTP error codes (4xx or 5xx)
            if response.status_code == 204: # No Content
                return {"status": "success", "message": "Update successful, no content returned."}
            # If other success codes might return JSON (e.g. 200), handle them here.
            # For now, assume 204 is the primary success for SPARQL UPDATE.
            # If a response body is expected for other success codes, parse it:
            try:
                return response.json()
            except json.JSONDecodeError:
                # Handle cases where a 2xx response might not have a JSON body
                return {"status": "success", "message": f"Update returned status {response.status_code} with non-JSON body."}
        else:
            self.graph.update(sparql_update)
            return {"status": "success"}
            
    def onto_validate(self, shapes_graph=None):
        """Validate graph using SHACL"""
        if not shapes_graph:
            shapes_graph = self._create_default_shapes()
            
        conforms, results_graph, results_text = validate(
            self.graph,
            shacl_graph=shapes_graph,
            ont_graph=None,
            inference='rdfs',
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            meta_shacl=False,
            debug=False,
            js=False
        )
        
        return {
            'conforms': conforms,
            'results': results_text
        }
        
    def _create_default_shapes(self):
        """Create default SHACL shapes for validation"""
        shapes_graph = Graph()
        
        # Module shape
        module_shape = GUIDANCE.ModuleShape
        shapes_graph.add((module_shape, RDF.type, SH.NodeShape))
        shapes_graph.add((module_shape, SH.targetClass, GUIDANCE.CoreModule))
        
        # Label property shape
        label_property = BNode()
        shapes_graph.add((module_shape, SH.property, label_property))
        shapes_graph.add((label_property, SH.path, RDFS.label))
        shapes_graph.add((label_property, SH.minCount, Literal(1)))
        shapes_graph.add((label_property, SH.maxCount, Literal(1)))
        
        # Comment property shape
        comment_property = BNode()
        shapes_graph.add((module_shape, SH.property, comment_property))
        shapes_graph.add((comment_property, SH.path, RDFS.comment))
        shapes_graph.add((comment_property, SH.minCount, Literal(1)))
        shapes_graph.add((comment_property, SH.maxCount, Literal(1)))
        
        return shapes_graph

    # Backward compatibility aliases
    def load_ontology(self, ontology_path):
        return self.onto_load_ontology(ontology_path)
    
    def query(self, sparql_query):
        return self.sparql_query(sparql_query)
    
    def update(self, sparql_update):
        return self.sparql_update(sparql_update)
    
    def validate(self, shapes_graph=None):
        return self.onto_validate(shapes_graph)


def main():
    # Example usage
    client = SPARQLClient()
    client.load_ontology("guidance.ttl")
    
    # Query for modules
    query = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    SELECT ?module ?label ?comment WHERE {
        ?module a guidance:CoreModule ;
                rdfs:label ?label ;
                rdfs:comment ?comment .
    }
    """
    
    results = client.query(query)
    print(json.dumps(results, indent=2))
    
    # Validate
    validation_result = client.validate()
    print(json.dumps(validation_result, indent=2))


if __name__ == "__main__":
    main()
