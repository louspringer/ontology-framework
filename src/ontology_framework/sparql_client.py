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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
SH = Namespace("http://www.w3.org/ns/shacl#")


class SPARQLClient:
    def __init__(self, endpoint_url=None, graph=None):
        self.endpoint_url = endpoint_url
        self.graph = graph or Graph()
        
    def onto_load_ontology(self, ontology_path):
        """Load ontology into the graph"""
        self.graph.parse(ontology_path, format="turtle")
        logger.info(f"Loaded ontology from {ontology_path}")
        
    def sparql_query(self, sparql_query):
        """Execute SPARQL query"""
        if self.endpoint_url:
            response = requests.post(
                self.endpoint_url,
                data={'query': sparql_query},
                headers={'Accept': 'application/sparql-results+json'}
            )
            return response.json()
        else:
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
        if self.endpoint_url:
            response = requests.post(
                self.endpoint_url,
                data={'update': sparql_update},
                headers={'Content-Type': 'application/sparql-update'}
            )
            return response.json()
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
