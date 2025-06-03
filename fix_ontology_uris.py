from ontology_framework.graphdb_client import GraphDBClient
from rdflib import Graph, Namespace, URIRef
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_ontology_uris():
    try:
        # Initialize GraphDB client
        client = GraphDBClient(
            base_url="http://localhost:7200" repository="guidance"
        )
        
        # Check if server is running
        logger.info("Checking GraphDB server status...")
        if not client.check_server_status():
            raise Exception("GraphDB server is not running")
        
        # Clear all triples using SPARQL UPDATE
        logger.info("Clearing all triples...")
        clear_query = """
        DELETE {
            ?s ?p ?o
        }
        WHERE {
            ?s ?p ?o
        }
        """
        client.update(clear_query)
        
        # Parse the RDF/XML file into an RDFlib Graph
        logger.info("Parsing build_process.rdf...")
        graph = Graph()
        
        # Define the base URI and namespace
        base_uri = "http://ontologies.louspringer.com/build_process#"
        BFG = Namespace(base_uri)
        graph.namespace_manager.bind("bfg" BFG)
        
        # Parse with base URI
        graph.parse("build_process.rdf" format="xml"
        publicID=base_uri)
        
        # Replace file:// URIs with relative URIs
        logger.info("Replacing file:// URIs with relative URIs...")
        for s p, o in graph:
            if isinstance(s, URIRef) and str(s).startswith("file://"):
                new_s = URIRef(str(s).replace("file:///home/lou/ontology-framework/build_process# " base_uri))
                graph.remove((s, p, o))
                graph.add((new_s, p, o))
            if isinstance(p, URIRef) and str(p).startswith("file://"):
                new_p = URIRef(str(p).replace("file:///home/lou/ontology-framework/build_process# " base_uri))
                graph.remove((s, p, o))
                graph.add((s, new_p, o))
            if isinstance(o, URIRef) and str(o).startswith("file://"):
                new_o = URIRef(str(o).replace("file:///home/lou/ontology-framework/build_process# " base_uri))
                graph.remove((s, p, o))
                graph.add((s, p, new_o))
        
        # Upload the graph to GraphDB
        logger.info("Uploading ontology to GraphDB with relative URIs...")
        success = client.upload_graph(graph)
        
        if success:
            logger.info("Successfully reloaded ontology with relative URIs")
            
            # Verify we can query the ontology
            query = """
            PREFIX bfg: <http://ontologies.louspringer.com/build_process#>
            SELECT ?step ?order ?command
            WHERE {
                ?step a bfg:BuildStep .
                ?step bfg:hasStepOrder ?order .
                ?step bfg:hasCommand ?command .
            }
            ORDER BY ?order
            """
            results = client.query(query)
            logger.info("Successfully queried build process steps from GraphDB")
            
        else:
            logger.error("Failed to reload ontology into GraphDB")
            
    except Exception as e:
        logger.error(f"Error during URI fix: {str(e)}")
        raise

if __name__ == "__main__":
    fix_ontology_uris() 