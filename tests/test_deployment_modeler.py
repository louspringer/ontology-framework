# !/usr/bin/env python3
"""
Tests for the DeploymentModeler class.
"""

import unittest
from unittest.mock import patch, MagicMock
from ontology_framework.deployment_modeler import DeploymentModeler
from ontology_framework.validation import ValidationManager
from ontology_framework.exceptions import ValidationError


class TestDeploymentModeler(unittest.TestCase):
    """Test cases for the DeploymentModeler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.modeler = DeploymentModeler()
        self.test_config = {
            "name": "testapp",
            "environment": "dev",
            "port": 8080,
            "replicas": 1,
            "memory_request": "256Mi",
            "cpu_request": "100m",
            "memory_limit": "512Mi",
            "cpu_limit": "200m"
        }

    def test_initialization(self):
        """Test that DeploymentModeler initializes correctly."""
        self.assertIsNotNone(self.modeler.graph)
        self.assertIsNotNone(self.modeler.error_handler)
        self.assertIsNotNone(self.modeler.validation_manager)

    def test_get_deployment_config(self):
        """Test retrieving deployment configuration."""
        config = self.modeler.get_deployment_config("testapp", "dev")
        self.assertEqual(config["name"], "testapp")
        self.assertEqual(config["environment"], "dev")
        self.assertEqual(config["port"], 8080)
        self.assertEqual(config["replicas"], 1)
        self.assertEqual(config["memory_request"], "256Mi")
        self.assertEqual(config["cpu_request"], "100m")
        self.assertEqual(config["memory_limit"], "512Mi")
        self.assertEqual(config["cpu_limit"], "200m")

    def test_validate_deployment_success(self):
        """Test successful deployment validation."""
        result = self.modeler.validate_deployment(self.test_config)
        self.assertTrue(result["is_valid"])
        self.assertEqual(len(result["issues"]), 0)
        
    def test_validate_deployment_failure(self):
        """Test failed deployment validation."""
        # Test missing required field
        invalid_config = self.test_config.copy()
        del invalid_config["name"]
        result = self.modeler.validate_deployment(invalid_config)
        self.assertFalse(result["is_valid"])
        self.assertTrue(any("Missing required field: name" in issue for issue in result["issues"]))
        
        # Test invalid port range
        invalid_config = self.test_config.copy()
        invalid_config["port"] = 80
        result = self.modeler.validate_deployment(invalid_config)
        self.assertFalse(result["is_valid"])
        self.assertTrue(any("Port must be between 1024 and 65535" in issue for issue in result["issues"]))
        
        # Test invalid environment
        invalid_config = self.test_config.copy()
        invalid_config["environment"] = "invalid"
        result = self.modeler.validate_deployment(invalid_config)
        self.assertFalse(result["is_valid"])
        self.assertTrue(any("Environment must be one of: dev, staging, prod" in issue for issue in result["issues"]))
        
        # Test invalid replicas
        invalid_config = self.test_config.copy()
        invalid_config["replicas"] = 0
        result = self.modeler.validate_deployment(invalid_config)
        self.assertFalse(result["is_valid"])
        self.assertTrue(any("Replicas must be at least 1" in issue for issue in result["issues"]))
        
        # Test invalid name format
        invalid_config = self.test_config.copy()
        invalid_config["name"] = "invalid-name"
        result = self.modeler.validate_deployment(invalid_config)
        self.assertFalse(result["is_valid"])
        self.assertTrue(any("Name must contain only alphanumeric characters" in issue for issue in result["issues"]))

    def test_generate_deployment_artifacts(self):
        """Test generating deployment artifacts."""
        artifacts = self.modeler.generate_deployment_artifacts(self.test_config)
        self.assertIn("kubernetes", artifacts)
        self.assertIn("docker_compose", artifacts)
        self.assertIn("deploy_script", artifacts)
        self.assertIn("apiVersion: apps/v1", artifacts["kubernetes"])
        self.assertIn("version: '3'", artifacts["docker_compose"])
        self.assertIn("#!/bin/bash", artifacts["deploy_script"])

    @patch('ontology_framework.deployment_modeler.DeploymentModeler._load_core_ontologies')
    def test_load_core_ontologies_error(self, mock_load):
        """Test error handling during core ontologies loading."""
        mock_load.side_effect = Exception("Failed to load ontologies")
        with self.assertLogs(level='ERROR') as log:
            modeler = DeploymentModeler()  # This should not raise an exception
            self.assertIsNotNone(modeler)
            self.assertIn("Failed to load core ontologies", log.output[0])
            errors = modeler.error_handler.get_errors()
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0]["error_type"], "RuntimeError")
            self.assertEqual(errors[0]["message"], "Failed to load core ontologies")
            self.assertEqual(errors[0]["severity"], "HIGH")

    def test_generate_k8s_deployment(self):
        """Test generating Kubernetes deployment configuration."""
        k8s_config = self.modeler._generate_k8s_deployment(self.test_config)
        self.assertIn("apiVersion: apps/v1", k8s_config)
        self.assertIn("kind: Deployment", k8s_config)

    def test_generate_docker_compose(self):
        """Test generating Docker Compose configuration."""
        compose_config = self.modeler._generate_docker_compose(self.test_config)
        self.assertIn("version: '3'", compose_config)

    def test_generate_deploy_script(self):
        """Test generating deployment script."""
        deploy_script = self.modeler._generate_deploy_script(self.test_config)
        self.assertIn("#!/bin/bash", deploy_script)


if __name__ == '__main__':
    unittest.main() 