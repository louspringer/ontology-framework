#!/usr/bin/env python3
"""Fix guidance ontology using semantic web tools."""

from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
import pyshacl
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_guidance_ontology():
    """Fix guidance ontology using RDFlib and PyShacl."""
    # Load the guidance ontology
    g = Graph()
    g.parse('guidance.ttl', format='turtle')
    
    # Define namespaces
    GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
    
    # Find the ClassHierarchyCheck node
    class_hierarchy_check = GUIDANCE.ClassHierarchyCheck
    
    # Remove existing hasTarget triple
    g.remove((class_hierarchy_check, GUIDANCE.hasTarget, None))
    
    # Add correct hasTarget triple with xsd:anyURI datatype
    target_uri = "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#ClassHierarchy"
    g.add((class_hierarchy_check, GUIDANCE.hasTarget, Literal(target_uri, datatype=XSD.anyURI)))
    
    # Validate using PyShacl
    conforms, results_graph, results_text = pyshacl.validate(
        g,
        shacl_graph=g,  # Using the same graph as it contains the SHACL shapes
        ont_graph=None,
        inference='rdfs',
        abort_on_first=False,
        allow_warnings=True,
        meta_shacl=False,
        advanced=True,
        debug=False
    )
    
    if conforms:
        logger.info("Validation successful, saving changes...")
        g.serialize('guidance.ttl', format='turtle')
        return True
    else:
        logger.error(f"Validation failed:\n{results_text}")
        return False

if __name__ == '__main__':
    fix_guidance_ontology() 