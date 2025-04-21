#!/usr/bin/env python3
"""Deployment modeling tool for managing deployment configurations."""

import logging
import os
from typing import Dict, List, Optional, Any
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS, OWL
from rdflib.plugins.sparql import prepareQuery
from ontology_framework.jena_client import JenaFusekiClient
from ontology_framework.validation import SHACLValidator

class DeploymentModeler:
    """Tool for managing deployment configurations using ontologies."""
    
    def __init__(self, base_url: str = "http://localhost:3030"):
        """Initialize the deployment modeler.
        
        Args:
            base_url: Base URL for the SPARQL endpoint
        """
        self.logger = logging.getLogger(__name__)
        self.client = JenaFusekiClient(base_url)
        self.validator = SHACLValidator()
        self.graph = Graph()
        
        # Load core ontologies
        self._load_core_ontologies()
        
    def _load_core_ontologies(self):
        """Load core deployment ontologies."""
        try:
            # Load deployment configuration ontology
            self.graph.parse("guidance/modules/deployment_config.ttl", format="turtle")
            self.graph.parse("guidance/modules/deployment.ttl", format="turtle")
            self.graph.parse("guidance/modules/deployment_validation.ttl", format="turtle")
            
            self.logger.info("Loaded core deployment ontologies")
        except Exception as e:
            self.logger.error(f"Failed to load core ontologies: {e}")
            raise
            
    def get_deployment_config(self, environment: str) -> Dict[str, Any]:
        """Get deployment configuration for a specific environment.
        
        Args:
            environment: Environment name (dev, staging, prod)
            
        Returns:
            Dictionary containing deployment configuration
        """
        try:
            query = prepareQuery("""
                PREFIX ns1: <http://example.org/guidance#>
                SELECT ?config ?property ?value
                WHERE {
                    ?config a ns1:EnvironmentConfig ;
                        rdfs:label ?env ;
                        ?property ?value .
                    FILTER (str(?env) = ?env_name)
                }
            """)
            
            results = self.graph.query(query, initBindings={'env_name': Literal(environment)})
            config = {}
            
            for row in results:
                prop = str(row['property']).split('#')[-1]
                config[prop] = str(row['value'])
                
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to get deployment config: {e}")
            raise
            
    def validate_deployment(self, config: Dict[str, Any]) -> List[str]:
        """Validate deployment configuration against SHACL rules.
        
        Args:
            config: Deployment configuration to validate
            
        Returns:
            List of validation errors, empty if valid
        """
        try:
            # Convert config to RDF
            config_graph = Graph()
            config_uri = URIRef(f"http://example.org/config/{config.get('name', 'default')}")
            
            for key, value in config.items():
                prop = URIRef(f"http://example.org/guidance#{key}")
                config_graph.add((config_uri, prop, Literal(value)))
                
            # Validate against SHACL rules
            return self.validator.validate(config_graph)
            
        except Exception as e:
            self.logger.error(f"Failed to validate deployment: {e}")
            raise
            
    def generate_deployment_artifacts(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate deployment artifacts from configuration.
        
        Args:
            config: Deployment configuration
            
        Returns:
            Dictionary of artifact names to content
        """
        try:
            artifacts = {}
            
            # Generate Kubernetes deployment
            k8s_deployment = self._generate_k8s_deployment(config)
            artifacts['deployment.yaml'] = k8s_deployment
            
            # Generate Docker Compose
            docker_compose = self._generate_docker_compose(config)
            artifacts['docker-compose.yml'] = docker_compose
            
            # Generate deployment script
            deploy_script = self._generate_deploy_script(config)
            artifacts['deploy.sh'] = deploy_script
            
            return artifacts
            
        except Exception as e:
            self.logger.error(f"Failed to generate artifacts: {e}")
            raise
            
    def _generate_k8s_deployment(self, config: Dict[str, Any]) -> str:
        """Generate Kubernetes deployment YAML."""
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {config.get('name', 'ontology-framework')}
spec:
  replicas: {config.get('replicas', 1)}
  selector:
    matchLabels:
      app: {config.get('name', 'ontology-framework')}
  template:
    metadata:
      labels:
        app: {config.get('name', 'ontology-framework')}
    spec:
      containers:
      - name: {config.get('name', 'ontology-framework')}
        image: {config.get('image', 'docker.io/louspringer/ontology-framework-dev:latest')}
        imagePullPolicy: Always
        resources:
          requests:
            memory: "{config.get('memory_request', '64Mi')}"
            cpu: "{config.get('cpu_request', '250m')}"
          limits:
            memory: "{config.get('memory_limit', '128Mi')}"
            cpu: "{config.get('cpu_limit', '500m')}"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: {config.get('name', 'ontology-framework')}-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: {config.get('name', 'ontology-framework')}"""
        
    def _generate_docker_compose(self, config: Dict[str, Any]) -> str:
        """Generate Docker Compose YAML."""
        return f"""version: '3'
services:
  {config.get('name', 'ontology-framework')}:
    image: {config.get('image', 'docker.io/louspringer/ontology-framework-dev:latest')}
    ports:
      - "{config.get('port', '80')}:80"
    environment:
      - NODE_ENV={config.get('environment', 'development')}
    volumes:
      - ./data:/app/data
    networks:
      - {config.get('network', 'ontology-network')}

networks:
  {config.get('network', 'ontology-network')}:
    driver: bridge"""
        
    def _generate_deploy_script(self, config: Dict[str, Any]) -> str:
        """Generate deployment shell script."""
        return f"""#!/bin/bash
# Deployment script for {config.get('name', 'ontology-framework')}

# Set environment variables
export NODE_ENV={config.get('environment', 'development')}
export PORT={config.get('port', '80')}

# Pull latest image
docker pull {config.get('image', 'docker.io/louspringer/ontology-framework-dev:latest')}

# Deploy using docker-compose
docker-compose up -d

# Wait for service to be ready
sleep 10

# Verify deployment
curl -f http://localhost:{config.get('port', '80')}/health || exit 1

echo "Deployment completed successfully"
""" 