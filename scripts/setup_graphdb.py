#!/usr/bin/env python3
"""Script to set up GraphDB repository."""

import logging
from pathlib import Path
from rdflib import Graph
from ontology_framework.graphdb_client import GraphDBClient

def main():
    """Set up GraphDB repository."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize GraphDB client
    client = GraphDBClient(
        base_url="http://localhost:7200"
    )
    
    repository_name = "guidance"
    
    try:
        # Check server status
        logger.info("Checking GraphDB server status...")
        if not client.check_server_status():
            raise RuntimeError("GraphDB server is not running")
            
        # Create repository if it doesn't exist
        repositories = client.list_repositories()
        if not any(repo["id"] == repository_name for repo in repositories):
            logger.info(f"Creating repository {repository_name}...")
            client.create_repository(repository_name, "Guidance Repository")
            logger.info("Repository created successfully")
        else:
            logger.info(f"Repository {repository_name} already exists")
        
        # Update client to use the guidance repository
        client.repository = repository_name
        
        # Load guidance ontology
        guidance_path = Path("guidance.ttl")
        if guidance_path.exists():
            logger.info("Loading guidance ontology...")
            # Load TTL file into RDFlib Graph
            g = Graph()
            g.parse(str(guidance_path), format="turtle")
            # Upload to GraphDB
            client.upload_graph(g)
            logger.info("Guidance ontology loaded successfully")
        else:
            logger.error("guidance.ttl not found!")
            raise FileNotFoundError("guidance.ttl not found!")
            
    except Exception as e:
        logger.error(f"Failed to set up GraphDB: {e}")
        raise

if __name__ == "__main__":
    main() 