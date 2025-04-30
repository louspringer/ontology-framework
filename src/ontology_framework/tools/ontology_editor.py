from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL
import os

def add_validation_rule(rule_name: str, rule_value: str):
    """Add a new validation rule to the ontology using RDFlib."""
    # Create a new graph
    g = Graph()
    
    # Define namespaces
    ONT = Namespace("http://example.org/ontology#")
    g.bind("ont", ONT)
    
    # Load existing ontology if it exists
    ontology_path = os.path.join(os.path.dirname(__file__), "..", "ontologies", "validation_rules.ttl")
    if os.path.exists(ontology_path):
        g.parse(ontology_path, format="turtle")
    
    # Create the new validation rule
    rule_uri = ONT[rule_name]
    g.add((rule_uri, RDF.type, ONT.ValidationRule))
    g.add((rule_uri, RDFS.label, Literal(rule_name)))
    g.add((rule_uri, ONT.hasValue, Literal(rule_value)))
    
    # Save the updated ontology
    g.serialize(destination=ontology_path, format="turtle")

def query_validation_rules():
    """Query existing validation rules using SPARQL."""
    g = Graph()
    ontology_path = os.path.join(os.path.dirname(__file__), "..", "ontologies", "validation_rules.ttl")
    if os.path.exists(ontology_path):
        g.parse(ontology_path, format="turtle")
    
    query = """
    SELECT ?rule ?value
    WHERE {
        ?rule a ont:ValidationRule ;
              ont:hasValue ?value .
    }
    """
    
    results = g.query(query)
    return [(str(rule), str(value)) for rule, value in results]

if __name__ == "__main__":
    # Add the ONTOLOGY validation rule
    add_validation_rule("ONTOLOGY", "ontology") 