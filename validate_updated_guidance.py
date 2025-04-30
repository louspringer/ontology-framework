import logging
from rdflib import Graph
from pyshacl import validate

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('validation.log'),
        logging.StreamHandler()
    ]
)

def log_graph_contents(graph, name):
    """Log the contents of a graph for debugging."""
    logging.info(f"\nContents of {name} graph:")
    for s, p, o in graph:
        logging.debug(f"Subject: {s}")
        logging.debug(f"Predicate: {p}")
        logging.debug(f"Object: {o}")
        logging.debug("---")

def main():
    try:
        logging.info("Starting validation process")
        
        # Load the updated ontology
        logging.info("Loading data graph from guidance_updated.ttl")
        data_graph = Graph()
        data_graph.parse("guidance_updated.ttl", format="turtle")
        log_graph_contents(data_graph, "data")
        
        # The shapes are included in the same file
        shapes_graph = data_graph
        logging.info("Using data graph as shapes graph")
        log_graph_contents(shapes_graph, "shapes")
        
        # Run validation with detailed logging
        logging.info("Starting SHACL validation")
        conforms, results_graph, results_text = validate(
            data_graph,
            shacl_graph=shapes_graph,
            inference='rdfs',
            debug=True,
            meta_shacl=True,
            advanced=True
        )
        
        # Log validation results
        logging.info("\nValidation Results:")
        logging.info(results_text)
        logging.info(f"\nConforms: {conforms}")
        
        # Log detailed validation report
        if not conforms:
            logging.error("Validation failed. Detailed report:")
            for result in results_graph:
                logging.error(f"Validation error: {result}")
        
    except Exception as e:
        logging.error(f"Error during validation: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 