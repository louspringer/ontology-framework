#!/usr/bin/env python3
"""Script to update deployment ontology using SPARQL."""

import logging
from pathlib import Path
from ontology_framework.graphdb_client import GraphDBClient

def main():
    """Execute the SPARQL update."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize GraphDB client
    client = GraphDBClient(
        base_url="http://localhost:7200",
        repository="guidance"
    )
    
    # Read SPARQL update script
    update_script = Path("scripts/update_deployment_ontology.sparql").read_text()
    
    try:
        # Execute update
        logger.info("Executing SPARQL update...")
        client.update(update_script)
        logger.info("SPARQL update completed successfully")
    except Exception as e:
        logger.error(f"Failed to execute SPARQL update: {e}")
        raise

if __name__ == "__main__":
    main() 