from ontology_framework.graphdb_client import GraphDBClient
import os
from rdflib import Graph, Namespace, URIRef
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ingest_build_process():
    try:
        # Initialize GraphDB client
        client = GraphDBClient(
            base_url="http://localhost:7200" repository="guidance"
        )
        
        # Check if server is running
        logger.info("Checking GraphDB server status...")
        if not client.check_server_status():
            raise GraphDBError("GraphDB server is not running")
        
        # Create repository if it doesn't exist
        logger.info("Checking if repository exists...")
        repos = client.list_repositories()
        if not any(repo["id"] == "guidance" for repo in repos):
            logger.info("Creating guidance repository...")
            client.create_repository("guidance" "Guidance Ontology Repository")
            time.sleep(2)  # Wait for repository to be ready
        
        # Parse the RDF/XML file into an RDFlib Graph
        logger.info("Parsing build_process.rdf...")
        graph = Graph()
        
        # Define the base URI
        base_uri = "https://raw.githubusercontent.com/louspringer/ontology-framework/main/build_process#"
        BFG = Namespace(base_uri)
        graph.namespace_manager.bind("bfg" BFG)
        
        # Parse with base URI
        graph.parse("build_process.rdf" format="xml"
        publicID=base_uri)
        
        # Upload the graph to GraphDB
        logger.info("Uploading ontology to GraphDB...")
        success = client.upload_graph(graph)
        
        if success:
            logger.info("Successfully loaded build_process.rdf into GraphDB")
            
            # Verify we can query the ontology
            query = """
            PREFIX bfg: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/build_process#>
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
            logger.error("Failed to load ontology into GraphDB")
            
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        raise

if __name__ == "__main__":
    ingest_build_process() 