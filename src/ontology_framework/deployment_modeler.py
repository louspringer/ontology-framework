# !/usr/bin/env python3
"""
Module for modeling and generating deployment configurations.
"""

import logging
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from rdflib import Graph
from .error_handler import ErrorHandler
from .validation import ValidationManager
from .exceptions import ValidationError, OntologyFrameworkError
import requests
import warnings
from .graphdb_client import GraphDBClient

logger = logging.getLogger(__name__)

class DeploymentModeler:
    """Modeler for deployment configurations."""
    def __init__(self, base_url: str):
        """Initialize the deployment modeler.
        
        Args:
            base_url: Base URL of the GraphDB server
        """
        self.client = GraphDBClient(base_url)

    def model_deployment(self, config: Dict[str, Any]) -> bool:
        """Model a deployment configuration.
        
        Args:
            config: Deployment configuration dictionary
        Returns:
            True if successful
        """
        try:
            # Create repository if it doesn't exist
            if not any(repo["id"] == config["repository"] for repo in self.client.list_repositories()):
                self.client.create_repository(config["repository"], config.get("title", "Deployment Repository"))
            # Set repository for client
            self.client.repository = config["repository"]
            # Load ontologies if specified
            if "ontologies" in config:
                for ontology_path in config["ontologies"]:
                    if Path(ontology_path).exists():
                        self.client.load_ontology(ontology_path)
                    else:
                        logger.warning(f"Ontology file not found: {ontology_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to model deployment: {e}")
            raise OntologyFrameworkError(f"Deployment modeling failed: {str(e)}")

    def validate_deployment(self, repository: str) -> bool:
        """Validate a deployment configuration.
        
        Args:
            repository: Repository name
        Returns:
            True if validation passes
        """
        try:
            self.client.repository = repository
            # Run validation query
            result = self.client.query("""
                PREFIX sh: <http://www.w3.org/ns/shacl#>
                ASK {
                    ?report a sh:ValidationReport ;
                        sh:conforms true .
                }
            """)
            return result["boolean"]
        except Exception as e:
            logger.error(f"Failed to validate deployment: {e}")
            raise OntologyFrameworkError(f"Deployment validation failed: {str(e)}")

    def clear_deployment(self, repository: str) -> bool:
        """Clear a deployment configuration.
        
        Args:
            repository: Repository name
        Returns:
            True if successful
        """
        try:
            self.client.repository = repository
            return self.client.clear_graph()
        except Exception as e:
            logger.error(f"Failed to clear deployment: {e}")
            raise OntologyFrameworkError(f"Deployment clearing failed: {str(e)}")

    def deploy_ontology(self, ontology_path: Union[str, Path], repository_name: str, context_uri: Optional[str] = None) -> bool:
        """Deploy an ontology to a specific repository in GraphDB.
        
        Args:
            ontology_path: Path to ontology file.
            repository_name: The name of the repository to deploy to.
            context_uri: Optional named graph URI (context) for the upload.
                         If None, uploads to the default graph of the repository.
        Returns:
            True if successful.
        """
        original_repo = self.client.repository
        try:
            self.client.repository = repository_name # Set context for the operation
            # Call load_ontology which handles parsing the path and then calls upload_graph
            return self.client.load_ontology(ontology_path, context_uri=context_uri)
        except Exception as e:
            logger.error(f"Failed to deploy ontology to repository '{repository_name}': {e}")
            raise OntologyFrameworkError(f"Deployment error: {str(e)}")
        finally:
            self.client.repository = original_repo # Restore original repository context

    def list_datasets(self) -> List[str]:
        """List all datasets in GraphDB.
        Returns:
            List of dataset names
        """
        try:
            return self.client.list_graphs()
        except Exception as e:
            logger.error(f"Failed to list datasets: {e}")
            raise OntologyFrameworkError(f"Failed to list datasets: {str(e)}")

    def get_dataset_info(self, dataset_name: str) -> Dict:
        """Get information about a dataset.
        Args:
            dataset_name: Name of dataset
        Returns:
            Dataset information
        """
        try:
            return self.client.get_graph_info(dataset_name)
        except Exception as e:
            logger.error(f"Failed to get dataset info: {e}")
            raise OntologyFrameworkError(f"Failed to get dataset info: {str(e)}")

    def count_triples(self, dataset_name: str) -> int:
        """Count triples in a dataset.
        Args:
            dataset_name: Name of dataset
        Returns:
            Number of triples
        """
        try:
            return self.client.count_triples(dataset_name)
        except Exception as e:
            logger.error(f"Failed to count triples: {e}")
            raise OntologyFrameworkError(f"Failed to count triples: {str(e)}")

    def get_deployment_config(self, app_name: str, environment: str) -> Dict[str, Any]:
        """
        Get deployment configuration for an application.
        Args:
            app_name: Name of the application
            environment: Target environment (e.g., dev staging prod)
        Returns:
            Dictionary containing deployment configuration
        """
        try:
            alphanumeric_name = ''.join(c for c in app_name if c.isalnum())
            if not alphanumeric_name:
                raise ValueError("Application name must contain at least one alphanumeric character")
            config = {
                "name": alphanumeric_name,
                "environment": environment,
                "port": 8080,
                "replicas": 1,
                "memory_request": "256Mi",
                "cpu_request": "100m",
                "memory_limit": "512Mi",
                "cpu_limit": "200m"
            }
            return config
        except Exception as e:
            logger.error(f"Error getting deployment config: {e}")
            raise OntologyFrameworkError(f"Deployment configuration error: {str(e)}")

    def generate_deployment_artifacts(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate deployment artifacts based on configuration.
        Args:
            config: Deployment configuration
        Returns:
            Dictionary containing generated artifacts
        """
        try:
            validation_result = self.validate_deployment(config["repository"])
            if not validation_result:
                return {}
            artifacts = {
                "kubernetes": self._generate_k8s_deployment(config),
                "docker_compose": self._generate_docker_compose(config),
                "deploy_script": self._generate_deploy_script(config)
            }
            return artifacts
        except Exception as e:
            logger.error(f"Failed to generate deployment artifacts: {e}")
            raise OntologyFrameworkError(f"Failed to generate deployment artifacts: {str(e)}")

    # Placeholder methods for artifact generation
    def _generate_k8s_deployment(self, config: Dict[str, Any]) -> str:
        return f"Kubernetes deployment for {config['name']}"

    def _generate_docker_compose(self, config: Dict[str, Any]) -> str:
        return f"Docker Compose for {config['name']}"

    def _generate_deploy_script(self, config: Dict[str, Any]) -> str:
        return f"Deploy script for {config['name']}"

class DeploymentError(Exception):
    pass
