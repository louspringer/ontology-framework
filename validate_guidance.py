#!/usr/bin/env python3
"""Script to validate the guidance ontology."""

from rdflib import Graph, Namespace
from pyshacl import validate
import sys

def validate_guidance():
    # Load the ontology and shapes
    data_graph = Graph()
    shapes_graph = Graph()
    
    # Load main ontology
    data_graph.parse("guidance.ttl", format="turtle")
    
    # Load test shapes
    shapes_graph.parse("tests/guidance_test.ttl", format="turtle")
    
    # Run validation
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        debug=True
    )
    
    print("\nValidation Results:")
    print(results_text)
    
    return conforms

if __name__ == "__main__":
    success = validate_guidance()
    sys.exit(0 if success else 1) 