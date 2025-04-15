#!/usr/bin/env python3
"""Deployment script using model-driven configuration."""

import logging
import os
import subprocess
import time
import requests
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, cast
from rdflib import Graph, Node, URIRef, Literal, Variable
from rdflib.query import ResultRow
from ontology_framework.jena_client import JenaFusekiClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DeploymentError(Exception):
    """Custom exception for deployment errors."""
    pass

def load_deployment_config() -> Dict[str, str]:
    """Load deployment configuration from ontology.

    Returns:
        Dictionary containing deployment configuration

    Raises:
        DeploymentError: If configuration is invalid or missing
    """
    try:
        graph = Graph()
        graph.parse("guidance/modules/deployment.ttl", format="turtle")
        
        query = """
        PREFIX ns1: <http://example.org/guidance#>
        SELECT ?name ?version ?port ?endpoint ?dataset
        WHERE {
            ?deployment a ns1:JenaFusekiDeployment ;
                ns1:hasServiceName ?name ;
                ns1:hasServiceVersion ?version ;
                ns1:hasServicePort ?port ;
                ns1:hasServiceEndpoint ?endpoint ;
                ns1:hasDatasetName ?dataset .
        }
        """
        
        results = list(graph.query(query))
        if not results:
            raise DeploymentError("No deployment configuration found")
        
        # Each result is a ResultRow containing rdflib terms
        result = cast(ResultRow, results[0])
        config = {
            "name": str(result['name']),
            "version": str(result['version']),
            "port": str(result['port']),
            "endpoint": str(result['endpoint']),
            "dataset": str(result['dataset'])
        }
        
        logger.info(f"Loaded deployment configuration: {config}")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load deployment configuration: {e}")
        raise DeploymentError(f"Configuration error: {e}")

def start_fuseki(config: Dict[str, str]) -> None:
    """Start Jena Fuseki server.

    Args:
        config: Deployment configuration

    Raises:
        DeploymentError: If server fails to start
    """
    try:
        logger.info("Starting Jena Fuseki server")
        
        # Start Docker container and capture output
        process = subprocess.Popen(
            ["docker-compose", "up", "-d"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Failed to start Docker container: {stderr}")
            raise DeploymentError(f"Docker error: {stderr}")
        
        logger.info("Docker container started successfully")
        logger.debug(f"Docker output: {stdout}")
        
        # Wait for server to start
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                health_check = f"{config['endpoint']}/$/ping"
                response = requests.get(health_check, timeout=5)
                if response.status_code == 200 and response.text.strip() == "pong":
                    logger.info("Fuseki server is running")
                    return
            except requests.RequestException as e:
                logger.debug(f"Health check attempt {attempt + 1} failed: {e}")
            time.sleep(2)
        
        raise DeploymentError("Fuseki server failed to start within timeout period")
        
    except Exception as e:
        logger.error(f"Failed to start Fuseki server: {e}")
        raise DeploymentError(f"Server start error: {e}")

def check_logs(config: Dict[str, str]) -> None:
    """Check Fuseki server logs for errors.

    Args:
        config: Deployment configuration

    Raises:
        DeploymentError: If critical errors are found in logs
    """
    try:
        # Get container logs
        process = subprocess.Popen(
            ["docker", "logs", config["name"]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Failed to get container logs: {stderr}")
            return
        
        # Check for critical errors
        error_patterns = [
            "ERROR",
            "Exception",
            "Failed to start",
            "Connection refused"
        ]
        
        for pattern in error_patterns:
            if pattern in stdout or pattern in stderr:
                logger.error(f"Found critical error in logs: {pattern}")
                logger.error(f"Log snippet: {stdout[:500]}...")
                raise DeploymentError(f"Critical error in logs: {pattern}")
        
        logger.info("No critical errors found in logs")
        
    except Exception as e:
        logger.error(f"Failed to check logs: {e}")
        raise DeploymentError(f"Log check error: {e}")

def load_ontologies(client: JenaFusekiClient) -> None:
    """Load ontologies into Fuseki.

    Args:
        client: Jena Fuseki client

    Raises:
        DeploymentError: If ontology loading fails
    """
    try:
        logger.info("Loading ontologies")
        
        # Load all ontology files
        ontology_dir = os.path.join("guidance", "modules")
        for file in os.listdir(ontology_dir):
            if file.endswith(".ttl"):
                file_path = os.path.join(ontology_dir, file)
                try:
                    client.load_ontology(file_path)
                    logger.info(f"Loaded ontology: {file}")
                except Exception as e:
                    logger.error(f"Failed to load ontology {file}: {e}")
                    raise
        
        logger.info("All ontologies loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load ontologies: {e}")
        raise DeploymentError(f"Ontology loading error: {e}")

def main() -> None:
    """Main function."""
    start_time = datetime.now()
    logger.info(f"Starting deployment at {start_time}")
    
    try:
        # Load deployment configuration
        config = load_deployment_config()
        
        # Start Fuseki server
        start_fuseki(config)
        
        # Check server logs
        check_logs(config)
        
        # Initialize client
        client = JenaFusekiClient()
        
        # Load ontologies
        load_ontologies(client)
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Deployment completed successfully in {duration}")
        
    except DeploymentError as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 