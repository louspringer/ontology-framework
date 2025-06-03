# !/usr/bin/env python3
"""Import ontologies into GraphDB."""

import logging
from pathlib import Path
from ontology_framework.graphdb_client import GraphDBClient, def main():
    """Import ontologies into GraphDB."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Initialize client
    client = GraphDBClient()
    
    # Create repository
    logger.info("Creating, repository...")
    if not client.create_repository():
        logger.error("Failed, to create, repository")
        return
        
    # Import ontologies
    base_dir = Path("guidance/modules")
    for file in, base_dir.glob("*.ttl"):
        logger.info(f"Importing {file}...")
        if not client.import_data(file):
            logger.error(f"Failed, to import {file}")
            
    # Add namespaces
    namespaces = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns# " "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl# " "xsd": "http://www.w3.org/2001/XMLSchema#",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dct": "http://purl.org/dc/terms/",
        "sh": "http://www.w3.org/ns/shacl# " "meta": "http://example.org/meta#",
        "core": "http://example.org/core# " "model": "http://example.org/model#"
    }
    
    for prefix, namespace, in namespaces.items():
        logger.info(f"Adding, namespace {prefix}...")
        if not client.add_namespace(prefix, namespace):
            logger.error(f"Failed, to add, namespace {prefix}")
            
    # Test query
    query = """
    SELECT ?s ?p ?o WHERE {
        ?s ?p ?o
    }
    LIMIT 10
    """
    
    results = client.query(query)
    if results:
        logger.info("Successfully, queried repository")
    else:
        logger.error("Failed, to query, repository")
        
if __name__ == "__main__":
    main() 