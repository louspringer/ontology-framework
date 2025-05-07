#!/usr/bin/env python3
"""Script to fix the guidance ontology using RDFlib and PyShacl."""

import logging
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD
import pyshacl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_ontology(file_path: str) -> Graph:
    """Load the ontology from a file.
    
    Args:
        file_path: Path to the ontology file
        
    Returns:
        The loaded RDF graph
    """
    logger.info(f"Loading ontology from {file_path}")
    g = Graph()
    g.parse(file_path, format="turtle")
    return g

def remove_incorrect_triple(g: Graph) -> None:
    """Remove the incorrect :hasTarget triple from :ClassHierarchyCheck.
    
    Args:
        g: The RDF graph to modify
    """
    logger.info("Removing incorrect :hasTarget triple")
    ns = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    g.remove((URIRef(ns.ClassHierarchyCheck), URIRef(ns.hasTarget), URIRef(ns.ClassHierarchy)))

def add_correct_triple(g: Graph) -> None:
    """Add the correct :hasTarget triple with datatype xsd:anyURI.
    
    Args:
        g: The RDF graph to modify
    """
    logger.info("Adding correct :hasTarget triple")
    ns = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    g.add((URIRef(ns.ClassHierarchyCheck), URIRef(ns.hasTarget), 
           Literal("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#ClassHierarchy", datatype=XSD.anyURI)))

def validate_ontology(g: Graph) -> bool:
    """Validate the ontology using PyShacl.
    
    Args:
        g: The RDF graph to validate
        
    Returns:
        True if validation passes, False otherwise
    """
    logger.info("Validating ontology")
    conforms, results_graph, results_text = pyshacl.validate(g)
    if not conforms:
        logger.error(f"Validation failed:\n{results_text}")
    else:
        logger.info("Validation passed")
    return conforms

def save_ontology(g: Graph, file_path: str) -> None:
    """Save the ontology to a file.
    
    Args:
        g: The RDF graph to save
        file_path: Path to save the ontology to
    """
    logger.info(f"Saving ontology to {file_path}")
    g.serialize(destination=file_path, format="turtle")

def fix_guidance_ontology() -> None:
    """Fix the guidance ontology."""
    try:
        # Load the ontology
        g = load_ontology("guidance.ttl")
        
        # Remove incorrect triple
        remove_incorrect_triple(g)
        
        # Add correct triple
        add_correct_triple(g)
        
        # Validate changes
        if validate_ontology(g):
            # Save changes
            save_ontology(g, "guidance.ttl")
            logger.info("Successfully fixed and saved guidance ontology")
        else:
            logger.error("Failed to fix guidance ontology - validation failed")
            
    except Exception as e:
        logger.error(f"Failed to fix guidance ontology: {e}")
        raise

if __name__ == "__main__":
    fix_guidance_ontology() 