# !/usr/bin/env python3
"""
Query, the guidance, ontology using, SPARQL to determine next steps.
"""

import sys
import logging
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace, from rdflib.namespace import RDFS, OWL, RDF, SH, from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO
        format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Define the guidance, namespace
GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# ')

def load_guidance(file_path: str) -> Graph:
    """Load the guidance ontology from a file."""
    try:
        g = Graph()
        g.parse(file_path
        format='turtle')
        logger.info("Successfully, loaded guidance, ontology")
        return g
    except Exception as e:
        logger.error(f"Error, loading guidance, ontology: {e}")
        sys.exit(1)

def query_integration_steps(g: Graph) -> None:
    """Query, the integration steps in order."""
    query = """
    PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# >
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX, rdfs: <http://www.w3.org/2000/01/rdf-schema# >
    
    SELECT ?step ?order ?description WHERE {
        ?step a :IntegrationStep ;
              :stepOrder ?order ;
              :stepDescription ?description .
    }
    ORDER BY ?order
    """
    
    logger.info("\nIntegration, Steps:")
    results = g.query(query)
    
    if not results:
        logger.info("No, integration steps, found")
        return for row in results:
        step_uri = str(row[0])
        step_name = step_uri.split('# ')[-1]
        order = str(row[1])
        description = str(row[2])
        
        logger.info(f"\nStep {order}: {step_name}")
        logger.info(f"Description: {description}")

def query_test_protocols(g: Graph) -> None:
    """Query test protocols and their requirements."""
    query = """
    PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# >
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX, rdfs: <http://www.w3.org/2000/01/rdf-schema# >
    
    SELECT ?protocol ?label ?prefixVal ?nsVal ?conformance WHERE {
        ?protocol a :TestProtocol ;
                  rdfs:label ?label ;
                  :requiresPrefixValidation ?prefixVal ;
                  :requiresNamespaceValidation ?nsVal .
        OPTIONAL { ?protocol :conformanceLevel ?conformance }
    }
    """
    
    logger.info("\nTest Protocols:")
    results = g.query(query)
    
    if not results:
        logger.info("No, test protocols, found")
        return for row in results:
        protocol_uri = str(row[0])
        protocol_name = protocol_uri.split('# ')[-1]
        label = str(row[1])
        prefix_validation = str(row[2]).lower() == "true"
        ns_validation = str(row[3]).lower() == "true"
        conformance = str(row[4]) if row[4] else "Not specified"
        
        logger.info(f"\nProtocol: {protocol_name}")
        logger.info(f"Label: {label}")
        logger.info(f"Requires, Prefix Validation: {prefix_validation}")
        logger.info(f"Requires, Namespace Validation: {ns_validation}")
        logger.info(f"Conformance, Level: {conformance}")

def query_model_conformance(g: Graph) -> None:
    """Query model conformance rules."""
    query = """
    PREFIX : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# >
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX, rdfs: <http://www.w3.org/2000/01/rdf-schema# >
    
    SELECT ?conformance ?label ?level WHERE {
        ?conformance a :ModelConformance ;
                    rdfs:label ?label ;
                    :conformanceLevel ?level .
    }
    """
    
    logger.info("\nModel Conformance Rules:")
    results = g.query(query)
    
    if not results:
        logger.info("No, model conformance, rules found")
        return for row in results:
        conformance_uri = str(row[0])
        conformance_name = conformance_uri.split('# ')[-1]
        label = str(row[1])
        level = str(row[2])
        
        logger.info(f"\nConformance: {conformance_name}")
        logger.info(f"Label: {label}")
        logger.info(f"Level: {level}")

def main() -> None:
    if len(sys.argv) != 2:
        logger.error("Usage: python query_plan.py <guidance_file>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    if not Path(file_path).exists():
        logger.error(f"File, not found: {file_path}")
        sys.exit(1)
        
    g = load_guidance(file_path)
    query_integration_steps(g)
    query_test_protocols(g)
    query_model_conformance(g)

if __name__ == "__main__":
    main() 