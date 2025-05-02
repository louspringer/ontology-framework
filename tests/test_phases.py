"""Test suite for phases."""

import unittest
from pathlib import Path
import json
from typing import Dict, Any
from datetime import datetime
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from ontology_framework.modules.phases import (
    PhaseError,
    PhaseResult,
    PromptPhase,
    PlanPhase,
    DoPhase,
    CheckPhase,
    AdjustPhase
)

@pytest.fixture
def valid_context():
    """Create a valid context dictionary for testing."""
    return {
        "ontologyPath": "/path/to/ontology",
        "metadata": {"version": "1.0.0"},
        "validationRules": ["rule1", "rule2"],
        "targetFiles": ["file1.ttl", "file2.ttl"]
    }

@pytest.fixture
def invalid_context():
    """Create an invalid context dictionary for testing."""
    return {
        "ontologyPath": "/path/to/ontology",
        "metadata": {"version": "1.0.0"}
    }

def test_phase_error():
    """Test PhaseError exception."""
    with pytest.raises(PhaseError):
        raise PhaseError("Test error")

def test_phase_result():
    """Test PhaseResult dataclass."""
    result = PhaseResult(
        status="success",
        error=None,
        results={"test": "data"},
        start_time=datetime.now(),
        end_time=datetime.now(),
        rdf_graph="test graph"
    )
    assert result.status == "success"
    assert result.error is None
    assert result.results == {"test": "data"}
    assert isinstance(result.start_time, datetime)
    assert isinstance(result.end_time, datetime)
    assert result.rdf_graph == "test graph"

def test_prompt_phase_validation(valid_context, invalid_context):
    """Test context validation in PromptPhase."""
    phase = PromptPhase()
    
    # Test valid context
    phase._validate_context(valid_context)
    
    # Test invalid context
    with pytest.raises(PhaseError):
        phase._validate_context(invalid_context)
    
    # Test non-dict context
    with pytest.raises(PhaseError):
        phase._validate_context("not a dict")

def test_plan_phase(valid_context):
    """Test PlanPhase execution."""
    phase = PlanPhase()
    result = phase.execute(valid_context)
    
    assert result.status == "success"
    assert result.error is None
    assert isinstance(result.results, dict)
    assert "plan" in result.results
    assert isinstance(result.start_time, datetime)
    assert isinstance(result.end_time, datetime)
    assert isinstance(result.rdf_graph, str)
    
    # Verify RDF graph contents
    graph = Graph()
    graph.parse(data=result.rdf_graph, format="turtle")
    assert len(graph) > 0

def test_do_phase(valid_context):
    """Test DoPhase execution."""
    phase = DoPhase()
    result = phase.execute(valid_context)
    
    assert result.status == "success"
    assert result.error is None
    assert isinstance(result.results, dict)
    assert "filesChanged" in result.results
    assert "validationResults" in result.results
    assert isinstance(result.start_time, datetime)
    assert isinstance(result.end_time, datetime)
    assert isinstance(result.rdf_graph, str)

def test_check_phase(valid_context):
    """Test CheckPhase execution."""
    phase = CheckPhase()
    result = phase.execute(valid_context)
    
    assert result.status == "success"
    assert result.error is None
    assert isinstance(result.results, dict)
    assert "passed" in result.results
    assert "errors" in result.results
    assert isinstance(result.start_time, datetime)
    assert isinstance(result.end_time, datetime)
    assert isinstance(result.rdf_graph, str)

def test_adjust_phase(valid_context):
    """Test AdjustPhase execution."""
    phase = AdjustPhase()
    result = phase.execute(valid_context)
    
    assert result.status == "success"
    assert result.error is None
    assert isinstance(result.results, dict)
    assert "recommendations" in result.results
    assert "nextSteps" in result.results
    assert isinstance(result.start_time, datetime)
    assert isinstance(result.end_time, datetime)
    assert isinstance(result.rdf_graph, str)

def test_phase_error_handling(invalid_context):
    """Test error handling in all phases."""
    phases = [PlanPhase(), DoPhase(), CheckPhase(), AdjustPhase()]
    
    for phase in phases:
        result = phase.execute(invalid_context)
        assert result.status == "error"
        assert result.error is not None
        assert isinstance(result.start_time, datetime)
        assert isinstance(result.end_time, datetime)
        assert isinstance(result.rdf_graph, str)

def test_phase_instance_creation():
    """Test phase instance creation in RDF graph."""
    phase = PromptPhase()
    phase_uri = URIRef("http://example.org/phases/test")
    phase._create_phase_instance(phase_uri)
    
    assert (phase_uri, RDF.type, None) in phase.graph
    assert (phase_uri, RDFS.label, None) in phase.graph
    assert (phase_uri, None, None) in phase.graph  # hasStartTime 