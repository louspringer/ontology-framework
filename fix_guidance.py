#!/usr/bin/env python3
"""Fix guidance ontology using semantic web tools."""

import logging
from pathlib import Path
import rdflib
from rdflib import Graph, Namespace, RDF, XSD
from pyshacl import validate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_ontology(file_path):
    """Load ontology from file."""
    try:
        g = Graph()
        g.parse(file_path, format="turtle")
        return g
    except Exception as e:
        logger.error(f"Failed to load ontology: {e}")
        raise

def remove_incorrect_triple(graph, subject, predicate):
    """Remove incorrect triple from graph."""
    for s, p, o in graph.triples((subject, predicate, None)):
        graph.remove((s, p, o))
        logger.info(f"Removed incorrect triple: {s} {p} {o}")

def add_correct_triple(graph, subject, predicate, object_value, datatype):
    """Add correct triple to graph with datatype."""
    graph.add((subject, predicate, rdflib.Literal(object_value, datatype=datatype)))
    logger.info(f"Added correct triple: {subject} {predicate} {object_value}")

def validate_ontology(graph):
    """Validate ontology using PyShacl."""
    try:
        conforms, results_graph, results_text = validate(graph)
        if not conforms:
            logger.error(f"Validation failed: {results_text}")
            return False
        logger.info("Validation successful")
        return True
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False

def save_ontology(graph, file_path):
    """Save ontology to file."""
    try:
        graph.serialize(destination=file_path, format="turtle")
        logger.info(f"Saved ontology to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save ontology: {e}")
        raise

def fix_guidance_ontology():
    """Fix guidance ontology by correcting hasTarget property."""
    try:
        # Load ontology
        ontology_path = Path("guidance.ttl")
        graph = load_ontology(ontology_path)
        
        # Define namespaces
        GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
        
        # Fix ClassHierarchyCheck hasTarget property
        class_hierarchy_check = GUIDANCE.ClassHierarchyCheck
        has_target = GUIDANCE.hasTarget
        
        # Remove incorrect triple
        remove_incorrect_triple(graph, class_hierarchy_check, has_target)
        
        # Add correct triple with xsd:anyURI datatype
        add_correct_triple(
            graph,
            class_hierarchy_check,
            has_target,
            "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#ClassHierarchyCheck",
            XSD.anyURI
        )
        
        # Validate changes
        if not validate_ontology(graph):
            logger.error("Validation failed, not saving changes")
            return False
        
        # Save changes
        save_ontology(graph, ontology_path)
        return True
        
    except Exception as e:
        logger.error(f"Failed to fix guidance ontology: {e}")
        return False

if __name__ == "__main__":
    if fix_guidance_ontology():
        logger.info("Successfully fixed guidance ontology")
        exit(0)
    else:
        logger.error("Failed to fix guidance ontology")
        exit(1) 