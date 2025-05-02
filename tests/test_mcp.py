#!/usr/bin/env python3
"""Test suite for MCP."""

from typing import Dict, List, Any
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from ontology_framework.mcp.maintenance_server import MaintenanceServer
from ontology_framework.mcp.maintenance_config import MaintenanceConfig
from ontology_framework.mcp.maintenance_prompts import MaintenancePrompts
from rdflib import Graph, URIRef
from ontology_framework.modules.mcp_config import MCPConfig
from ontology_framework.modules.ontology_dependency_analyzer import OntologyDependencyAnalyzer

@pytest.fixture
def maintenance_server() -> MaintenanceServer:
    """Create a maintenance server instance."""
    return MaintenanceServer()

@pytest.fixture
def maintenance_prompts() -> MaintenancePrompts:
    """Create a maintenance prompts instance."""
    return MaintenancePrompts()

@pytest.fixture
def maintenance_config() -> MaintenanceConfig:
    """Create a maintenance config instance."""
    return MaintenanceConfig()

def test_server_initialization(maintenance_server: MaintenanceServer) -> None:
    """Test server initialization."""
    assert maintenance_server.model is not None
    assert isinstance(maintenance_server.model, Graph)

def test_get_maintenance_model(maintenance_server: MaintenanceServer) -> None:
    """Test getting maintenance model."""
    model = maintenance_server.get_maintenance_model()
    assert model is not None
    assert isinstance(model, str)

def test_get_validation_rules(maintenance_server: MaintenanceServer) -> None:
    """Test getting validation rules."""
    rules = maintenance_server.get_validation_rules()
    assert rules is not None
    assert len(rules) > 0

def test_get_maintenance_metrics(maintenance_server: MaintenanceServer) -> None:
    """Test getting maintenance metrics."""
    metrics = maintenance_server.get_maintenance_metrics()
    assert metrics is not None
    assert len(metrics) > 0

def test_validate_artifact(maintenance_server: MaintenanceServer) -> None:
    """Test artifact validation."""
    artifact_uri = "https://github.com/louspringer/ontology-framework/mcp#artifact1"
    result = maintenance_server.validate_artifact(artifact_uri)
    assert result["status"] == "valid"

def test_track_change(maintenance_server: MaintenanceServer) -> None:
    """Test change tracking."""
    change_id = "CHG-001"
    description = "Test change"
    affected_components = ["Component1", "Component2"]
    result = maintenance_server.track_change(change_id, description, affected_components)
    assert result["status"] == "tracked"
    assert result["change_id"] == change_id

def test_update_metric(maintenance_server: MaintenanceServer) -> None:
    """Test metric update."""
    metric_type = "validation_coverage"
    value = 0.95
    result = maintenance_server.update_metric(metric_type, value)
    assert result["status"] == "updated"
    assert result["metric"] == metric_type
    assert result["value"] == value

def test_prompts_initialization(maintenance_prompts: MaintenancePrompts) -> None:
    """Test prompts initialization."""
    assert maintenance_prompts is not None

def test_config_initialization(maintenance_config: MaintenanceConfig) -> None:
    """Test config initialization."""
    # Test core settings
    assert maintenance_config.conformance_level == "STRICT"
    assert isinstance(maintenance_config.validation_rules, dict)
    assert maintenance_config.ontology_path.name == "project_maintenance.ttl"
    
    # Test validation settings
    assert maintenance_config.validation_strategy == "SimilarityMatch"
    assert isinstance(maintenance_config.validation_path, dict)
    assert maintenance_config.validation_path["start_node"] == "ValidationRule"
    
    # Test quality settings
    assert maintenance_config.quality_threshold == 0.85
    assert "hasMessage" in maintenance_config.required_metadata
    assert "hasPriority" in maintenance_config.required_metadata 