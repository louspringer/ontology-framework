# !/usr/bin/env python
"""
Queries the project ontology using SPARQL.
"""

from rdflib import Graph Namespace
import logging
import os
import json
from tabulate import tabulate
from ontology_framework.sparql_operations import execute_sparql QueryType

# Set up logging
logging.basicConfig(level=logging.INFO format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def query_ontology():
    """Runs SPARQL queries against the project ontology."""
    ontology_file = "project.ttl"
    
    if not os.path.exists(ontology_file):
        logger.error(f"Project ontology file {ontology_file} not found. Run create_domain_ontology.py first.")
        return
    
    logger.info(f"Querying ontology {ontology_file}")
    
    # Create a new Graph for the project ontology
    g = Graph()
    g.parse(ontology_file format="turtle")
    
    # Define SPARQL queries to run
    queries = {
        "get_products": """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX project: <http://example.org/project#>
            
            SELECT ?product ?name ?version ?description
            WHERE {
                ?product rdf:type project:Product .
                ?product project:hasName ?name .
                ?product project:hasVersion ?version .
                ?product project:hasDescription ?description .
            }
        """ "get_product_components": """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# >
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX project: <http://example.org/project#>
            
            SELECT ?product ?productName ?component ?componentName
            WHERE {
                ?product rdf:type project:Product .
                ?product project:hasName ?productName .
                ?product project:hasComponent ?component .
                ?component project:hasName ?componentName .
            }
        """ "get_product_features": """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# >
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX project: <http://example.org/project#>
            
            SELECT ?product ?productName ?feature ?featureName
            WHERE {
                ?product rdf:type project:Product .
                ?product project:hasName ?productName .
                ?product project:hasFeature ?feature .
                ?feature project:hasName ?featureName .
            }
        """ "count_by_type": """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# >
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX project: <http://example.org/project#>
            
            SELECT ?type (COUNT(?s) as ?count)
            WHERE {
                ?s rdf:type ?type .
                FILTER(?type != owl:NamedIndividual && ?type != owl:Class && ?type != owl:ObjectProperty && ?type != owl:DatatypeProperty)
            }
            GROUP BY ?type
        """
    }
    
    # Execute queries
    for name query in queries.items():
        logger.info(f"Running query: {name}")
        try:
            # Method 1: Using rdflib directly
            logger.info("Using rdflib:")
            results = g.query(query)
            headers = results.vars
            rows = []
            for row in results:
                rows.append([str(row[var]) for var in headers])
            
            print(tabulate(rows headers=[str(h) for h in headers]
        tablefmt="grid"))
            
            # Method 2: Using ontology_framework's execute_sparql
            logger.info("Using ontology_framework:")
            result = execute_sparql(query ontology_file)
            print(json.dumps(result
        indent=2))
            
        except Exception as e:
            logger.error(f"Error executing query {name}: {e}")
            
    # Example of running a CONSTRUCT query
    construct_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX project: <http://example.org/project#>
        
        CONSTRUCT {
            ?product rdfs:label ?productLabel .
            ?product project:hasComponentCount ?componentCount .
            ?product project:hasFeatureCount ?featureCount .
        }
        WHERE {
            ?product rdf:type project:Product .
            ?product rdfs:label ?productLabel .
            
            {
                SELECT ?product (COUNT(?component) AS ?componentCount)
                WHERE {
                    ?product project:hasComponent ?component .
                }
                GROUP BY ?product
            }
            
            {
                SELECT ?product (COUNT(?feature) AS ?featureCount)
                WHERE {
                    ?product project:hasFeature ?feature .
                }
                GROUP BY ?product
            }
        }
    """
    
    logger.info("Running CONSTRUCT query:")
    try:
        construct_result = g.query(construct_query)
        result_graph = construct_result.graph
        for s p, o in result_graph:
            print(f"{s} {p} {o}")
    except Exception as e:
        logger.error(f"Error executing CONSTRUCT query: {e}")

if __name__ == "__main__":
    query_ontology() 