#!/usr/bin/env python3

import sys
import logging
from pathlib import Path
from datetime import datetime
from ontology_framework.mcp.core import MCPCore, ValidationContext
from bfg9k_manager import BFG9KManager
import json
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH, Namespace
from pyshacl import validate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_guidance():
    """Validate guidance.ttl using SHACL."""
    # Load guidance ontology
    data_graph = Graph()
    data_graph.parse("guidance.ttl", format="turtle")
    
    # Create SHACL shapes graph
    shapes_graph = Graph()
    
    # Define namespaces
    BFG9K = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
    
    # ValidationRule shape
    rule_shape = BNode()
    shapes_graph.add((rule_shape, RDF.type, SH.NodeShape))
    shapes_graph.add((rule_shape, SH.targetClass, URIRef("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#ValidationRule")))
    
    # Required properties
    for prop in ["hasMessage", "hasPriority", "hasTarget", "hasValidator"]:
        prop_shape = BNode()
        shapes_graph.add((rule_shape, SH.property, prop_shape))
        shapes_graph.add((prop_shape, SH.path, URIRef(f"https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#{prop}")))
        shapes_graph.add((prop_shape, SH.minCount, Literal(1)))
        shapes_graph.add((prop_shape, SH.maxCount, Literal(1)))
    
    # Validate
    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        ont_graph=None,
        inference='rdfs',
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
        meta_shacl=False,
        debug=False
    )
    
    return {
        'conforms': conforms,
        'results': results_text
    }

def main():
    print("Validating guidance.ttl...")
    try:
        result = validate_guidance()
        print("\nValidation Results:")
        print("-" * 50)
        print(f"Conforms: {'✓' if result['conforms'] else '✗'}")
        if result['results']:
            print("\nDetails:")
            print(result['results'])
    except Exception as e:
        print(f"Error validating guidance.ttl: {str(e)}")

if __name__ == "__main__":
    main() 