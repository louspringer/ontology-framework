from rdflib import Graph, Namespace, RDF, RDFS, OWL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_guidance_state():
    # Load all ontologies
    g = Graph()
    g.parse("guidance.ttl", format="turtle")
    
    # Define namespaces
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    CORE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/core#")
    MODEL = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/model#")
    
    # Check Legacy Support
    logger.info("Checking Legacy Support...")
    q1 = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    SELECT ?support ?mapping
    WHERE {
        ?support a guidance:LegacySupport .
        OPTIONAL { ?support guidance:hasLegacyMapping ?mapping }
    }
    """
    results = g.query(q1)
    for row in results:
        logger.info(f"Legacy Support: {row.support}, Mapping: {row.mapping}")
    
    # Check Module Registry
    logger.info("\nChecking Module Registry...")
    q2 = """
    PREFIX guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#>
    SELECT ?registry ?module
    WHERE {
        ?registry a guidance:ModuleRegistry .
        OPTIONAL { ?registry guidance:registeredModule ?module }
    }
    """
    results = g.query(q2)
    for row in results:
        logger.info(f"Registry: {row.registry}, Module: {row.module}")
    
    # Check Core Module Imports
    logger.info("\nChecking Core Module Imports...")
    q3 = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?module ?imported
    WHERE {
        ?module a owl:Ontology .
        OPTIONAL { ?module owl:imports ?imported }
    }
    """
    results = g.query(q3)
    for row in results:
        logger.info(f"Module: {row.module}, Imports: {row.imported}")
    
    # Check Model Module Classes
    logger.info("\nChecking Model Module Classes...")
    q4 = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?class ?label
    WHERE {
        ?class a owl:Class .
        OPTIONAL { ?class rdfs:label ?label }
    }
    """
    results = g.query(q4)
    for row in results:
        logger.info(f"Class: {row.class}, Label: {row.label}")

if __name__ == "__main__":
    analyze_guidance_state() 