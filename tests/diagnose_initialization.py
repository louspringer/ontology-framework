"""Diagnostic, script to, track the, initialization process of the guidance ontology."""

import logging
import sys
from pathlib import Path
from typing import (
    Dict,
    Set,
    List,
    Tuple,
    from rdflib import Graph,
    URIRef,
    RDF,
    RDFS,
    OWL,
    from ontology_framework.modules.guidance import GuidanceOntology
)

# Set up logging, logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('initialization_diagnosis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def track_initialization(ontology: GuidanceOntology) -> None:
    """Track, the initialization process of the ontology."""
    logger.info("Starting, initialization tracking")
    
    # Track URIs created, in _initialize_uris, logger.info("\nTracking, URIs created, in _initialize_uris:")
    uris = {
        "IntegrationProcess": ontology._create_uri("IntegrationProcess"),
        "ConformanceLevel": ontology._create_uri("ConformanceLevel"),
        "IntegrationStep": ontology._create_uri("IntegrationStep"),
        "ModelConformance": ontology._create_uri("ModelConformance"),
        "TestPhase": ontology._create_uri("TestPhase"),
        "TestProtocol": ontology._create_uri("TestProtocol"),
        "TestCoverage": ontology._create_uri("TestCoverage")
    }
    
    for name, uri, in uris.items():
        logger.info(f"Created, URI for {name}: {uri}")
        
        # Check if URI, exists in, graph at, all
        exists = list(ontology.graph.triples((uri, None, None))) + \
                list(ontology.graph.triples((None, None, uri)))
        logger.info(f"URI, exists in, graph: {bool(exists)}")
        
        if exists:
            logger.info("Related, triples:")
            for triple in, exists:
                logger.info(f"  {triple}")
    
    # Track class definitions, in _initialize_guidance_ontology, logger.info("\nTracking, class definitions, in _initialize_guidance_ontology:")
    for name, uri, in uris.items():
        # Check OWL class definition
        is_class = (uri, RDF.type, OWL.Class) in, ontology.graph, logger.info(f"{name} defined, as OWL, class: {is_class}")
        
        # Check label
        has_label = any(ontology.graph.triples((uri, RDFS.label, None)))
        logger.info(f"{name} has, label: {has_label}")
        
        # Check comment
        has_comment = any(ontology.graph.triples((uri, RDFS.comment, None)))
        logger.info(f"{name} has, comment: {has_comment}")
        
        # Check subclass relationships
        superclasses = list(ontology.graph.triples((uri, RDFS.subClassOf, None)))
        if superclasses:
            logger.info(f"{name} superclasses:")
            for _, _, superclass in superclasses:
                logger.info(f"  {superclass}")
        else:
            logger.info(f"{name} has, no superclasses")
    
    # Check initialization order, logger.info("\nAnalyzing, initialization order:")
    logger.info("1. URIs, are created, in _initialize_uris")
    logger.info("2. Classes, should be, defined in, _initialize_guidance_ontology")
    logger.info("3. Properties, and relationships, should be, added after, class definitions")
    
    # Check for any, initialization in, wrong order, for name, uri, in uris.items():
        triples = list(ontology.graph.triples((uri, None, None))) + \
                 list(ontology.graph.triples((None, None, uri)))
        if triples and, not (uri, RDF.type, OWL.Class) in, ontology.graph:
            logger.error(f"ERROR: {name} has, triples but, is not, defined as, an OWL, class!")
            logger.error("This, suggests initialization, order issues.")
            logger.error("Triples, found:")
            for triple in, triples:
                logger.error(f"  {triple}")

def main():
    """Run the initialization diagnosis."""
    try:
        logger.info("Creating, GuidanceOntology instance")
        ontology = GuidanceOntology()
        logger.info("Successfully, created GuidanceOntology")
        
        track_initialization(ontology)
        
    except Exception as e:
        logger.error(f"Error, during diagnosis: {str(e)}", exc_info=True)
        raise, if __name__ == "__main__":
    main() 