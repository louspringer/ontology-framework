#!/usr/bin/env python3
"""Script for deploying ontologies to GraphDB."""

import argparse
import logging
from pathlib import Path
from typing import List, Optional

from ontology_framework.graphdb_client import GraphDBClient, GraphDBError
from ontology_framework.deployment_modeler import DeploymentModeler, DeploymentError

def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def load_ontologies(client: GraphDBClient, ontology_dir: Path) -> None:
    """Load ontologies from a directory into GraphDB.
    
    Args:
        client: GraphDB client instance
        ontology_dir: Directory containing ontology files
    """
    for ontology_file in ontology_dir.glob("*.ttl"):
        try:
            logging.info(f"Loading ontology: {ontology_file}")
            client.load_ontology(ontology_file)
            logging.info(f"Successfully loaded {ontology_file}")
        except GraphDBError as e:
            logging.error(f"Failed to load {ontology_file}: {str(e)}")

def main() -> None:
    """Main entry point for deployment script."""
    parser = argparse.ArgumentParser(description="Deploy ontologies to GraphDB")
    parser.add_argument(
        "--base-url",
        default="http://localhost:7200",
        help="Base URL of GraphDB server"
    )
    parser.add_argument(
        "--repository",
        default="test",
        help="Repository name"
    )
    parser.add_argument(
        "--ontology-dir",
        type=Path,
        default=Path("ontologies"),
        help="Directory containing ontology files"
    )
    args = parser.parse_args()
    
    setup_logging()
    
    try:
        # Initialize clients
        client = GraphDBClient(args.base_url, args.repository)
        modeler = DeploymentModeler(args.base_url, args.repository)
        
        # Check server status
        logging.info("Checking GraphDB server status...")
        if not client.list_graphs():
            logging.warning("No graphs found in repository")
            
        # Load ontologies
        logging.info(f"Loading ontologies from {args.ontology_dir}")
        load_ontologies(client, args.ontology_dir)
        
        # Verify deployment
        logging.info("Verifying deployment...")
        datasets = modeler.list_datasets()
        for dataset in datasets:
            info = modeler.get_dataset_info(dataset)
            logging.info(f"Dataset {dataset}: {info['triples']} triples")
            
        logging.info("Deployment completed successfully")
        
    except (GraphDBError, DeploymentError) as e:
        logging.error(f"Deployment failed: {str(e)}")
        raise SystemExit(1)

if __name__ == "__main__":
    main() 