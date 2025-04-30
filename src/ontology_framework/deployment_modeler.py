#!/usr/bin/env python3
"""
Module for modeling and generating deployment configurations.
"""

import logging
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from rdflib import Graph
from .error_handler import ErrorHandler
from .validation import ValidationManager
from .exceptions import ValidationError
import requests
import warnings
from .sparql_client import SparqlClient
from .graphdb_client import GraphDBClient, GraphDBError

class DeploymentModeler:
    """Manages ontology deployment to GraphDB."""
    
    def __init__(self, base_url: str = "http://localhost:7200", repository: str = "test"):
        """Initialize the deployment modeler.
        
        Args:
            base_url: Base URL of the GraphDB server
            repository: Repository name
        """
        self.graphdb_client = GraphDBClient(base_url, repository)
        self.logger = logging.getLogger(__name__)
        
    def deploy_ontology(self, ontology_path: Union[str, Path], dataset_name: Optional[str] = None) -> bool:
        """Deploy an ontology to GraphDB.
        
        Args:
            ontology_path: Path to ontology file
            dataset_name: Optional dataset name
            
        Returns:
            True if successful
        """
        try:
            return self.graphdb_client.upload_graph(ontology_path, dataset_name)
        except GraphDBError as e:
            raise DeploymentError(f"Failed to deploy ontology: {str(e)}")
            
    def clear_dataset(self, dataset_name: str) -> bool:
        """Clear a dataset in GraphDB.
        
        Args:
            dataset_name: Name of dataset to clear
            
        Returns:
            True if successful
        """
        try:
            return self.graphdb_client.clear_graph(dataset_name)
        except GraphDBError as e:
            raise DeploymentError(f"Failed to clear dataset: {str(e)}")
            
    def list_datasets(self) -> List[str]:
        """List all datasets in GraphDB.
        
        Returns:
            List of dataset names
        """
        try:
            return self.graphdb_client.list_graphs()
        except GraphDBError as e:
            raise DeploymentError(f"Failed to list datasets: {str(e)}")
            
    def get_dataset_info(self, dataset_name: str) -> Dict:
        """Get information about a dataset.
        
        Args:
            dataset_name: Name of dataset
            
        Returns:
            Dataset information
        """
        try:
            return self.graphdb_client.get_graph_info(dataset_name)
        except GraphDBError as e:
            raise DeploymentError(f"Failed to get dataset info: {str(e)}")
            
    def count_triples(self, dataset_name: str) -> int:
        """Count triples in a dataset.
        
        Args:
            dataset_name: Name of dataset
            
        Returns:
            Number of triples
        """
        try:
            return self.graphdb_client.count_triples(dataset_name)
        except GraphDBError as e:
            raise DeploymentError(f"Failed to count triples: {str(e)}")

    def get_deployment_config(self, app_name: str, environment: str) -> Dict[str, Any]:
        """
        Get deployment configuration for an application.

        Args:
            app_name: Name of the application
            environment: Target environment (e.g., dev, staging, prod)

        Returns:
            Dictionary containing deployment configuration
        """
        try:
            # Ensure alphanumeric name
            alphanumeric_name = ''.join(c for c in app_name if c.isalnum())
            if not alphanumeric_name:
                raise ValueError("Application name must contain at least one alphanumeric character")

            # Default configuration
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
            self.error_handler.add_error(
                "ConfigurationError",
                f"Error getting deployment config: {str(e)}",
                "HIGH"
            )
            return {}

    def validate_deployment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate deployment configuration.

        Args:
            config: Deployment configuration to validate

        Returns:
            Dict containing validation result and any issues found
        """
        try:
            # Validate using all available rules
            validation_rules = ["required_fields", "numeric_ranges", "string_format"]
            result = self.validation_manager.validate(config, validation_rules)
            
            if isinstance(result, dict) and not result.get("is_valid", True):
                for issue in result.get("issues", []):
                    self.error_handler.add_error(
                        "ValidationError",
                        issue,
                        "HIGH"
                    )
                    
            return result
            
        except Exception as e:
            self.error_handler.add_error(
                "ValidationError",
                f"Error during validation: {str(e)}",
                "HIGH"
            )
            return {
                "is_valid": False,
                "issues": [f"Validation error: {str(e)}"]
            }

    def generate_deployment_artifacts(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate deployment artifacts based on configuration.

        Args:
            config: Deployment configuration

        Returns:
            Dictionary containing generated artifacts
        """
        try:
            validation_result = self.validate_deployment(config)
            if not validation_result["is_valid"]:
                return {}

            artifacts = {
                "kubernetes": self._generate_k8s_deployment(config),
                "docker_compose": self._generate_docker_compose(config),
                "deploy_script": self._generate_deploy_script(config)
            }
            return artifacts
        except Exception as e:
            self.error_handler.add_error(
                "ArtifactGenerationError",
                f"Error generating deployment artifacts: {str(e)}",
                "HIGH"
            )
            return {}

    def _generate_k8s_deployment(self, config: Dict[str, Any]) -> str:
        """Generate Kubernetes deployment configuration."""
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {config['name']}
spec:
  replicas: {config['replicas']}
  selector:
    matchLabels:
      app: {config['name']}
  template:
    metadata:
      labels:
        app: {config['name']}
    spec:
      containers:
      - name: {config['name']}
        resources:
          requests:
            memory: {config['memory_request']}
            cpu: {config['cpu_request']}
          limits:
            memory: {config['memory_limit']}
            cpu: {config['cpu_limit']}
        ports:
        - containerPort: {config['port']}"""

    def _generate_docker_compose(self, config: Dict[str, Any]) -> str:
        """Generate Docker Compose configuration."""
        return f"""version: '3'
services:
  {config['name']}:
    build: .
    ports:
      - "{config['port']}:{config['port']}"
    environment:
      - ENVIRONMENT={config['environment']}
    deploy:
      resources:
        limits:
          cpus: '{config['cpu_limit']}'
          memory: {config['memory_limit']}
        reservations:
          cpus: '{config['cpu_request']}'
          memory: {config['memory_request']}"""

    def _generate_deploy_script(self, config: Dict[str, Any]) -> str:
        """Generate deployment script."""
        return f"""#!/bin/bash
# Deployment script for {config['name']} in {config['environment']} environment

# Apply Kubernetes deployment
kubectl apply -f deployment.yaml

# Wait for deployment to be ready
kubectl rollout status deployment/{config['name']}

echo "Deployment of {config['name']} to {config['environment']} completed."""

class DeploymentError(Exception):
    """Exception raised for deployment-related errors."""
    pass 