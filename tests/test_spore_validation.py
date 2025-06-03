"""Tests for spore validation functionality."""

import pytest
from unittest.mock import patch, MagicMock
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.term import Node
from rdflib.namespace import RDF, RDFS, OWL
import logging
import traceback
from typing import Optional, Generator
import os
import shutil
from pathlib import Path
from src.ontology_framework.spore_integration import SporeIntegrator, GUIDANCE, CONFORMANCE_LEVELS
from src.ontology_framework.exceptions import ConformanceError
from src.ontology_framework.spore_validation import SporeValidator
from src.ontology_framework.exceptions import ValidationError

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Test namespaces
TEST = Namespace("http://test.example.org/")
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# ")

@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary directory for test data."""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return str(test_dir)

@pytest.fixture
def validator():
    """Create a SporeValidator instance for testing."""
    graph = Graph()
    validator = SporeValidator(graph=graph)
    return validator

@pytest.fixture
def integrator(test_data_dir):
    """Create a SporeIntegrator instance for testing."""
    return SporeIntegrator(test_data_dir)

@pytest.fixture
def spore_uri() -> URIRef:
    """Create a test spore URI."""
    return URIRef("http://example.org/test# TestSpore")

@pytest.fixture(name="integrator_with_data")
def create_integrator_with_data() -> SporeIntegrator:
    """Create a SporeIntegrator instance for testing."""
    test_data_dir = Path("test_data")
    test_data_dir.mkdir(exist_ok=True)
    
    # Create test graphs
    guidance_graph = Graph()
    spore_graph = Graph()
    
    # Add conformance levels to guidance graph
    for level_str, level_uri in CONFORMANCE_LEVELS.items():
        guidance_graph.add((level_uri, RDF.type, GUIDANCE.ConformanceLevel))
        guidance_graph.add((level_uri, GUIDANCE.conformanceLevel, Literal(level_str)))
        guidance_graph.add((level_uri, GUIDANCE.hasValidationRules, Literal("test, rules")))
        guidance_graph.add((level_uri, GUIDANCE.hasMinimumRequirements, Literal("test, requirements")))
        guidance_graph.add((level_uri, GUIDANCE.hasComplianceMetrics, Literal("test, metrics")))
    
    # Register test namespace in guidance ontology
    test_spore_uri: URIRef = URIRef("http://example.org/test-spore")
    guidance_graph.add((test_spore_uri, RDF.type, GUIDANCE.Namespace))
    guidance_graph.add((test_spore_uri, RDFS.label, Literal("Test, Namespace")))
    guidance_graph.add((test_spore_uri, RDFS.comment, Literal("A, test namespace, for validation")))
    
    # Bind test and guidance namespaces
    guidance_graph.bind("test", TEST)
    guidance_graph.bind("guidance", GUIDANCE)
    
    # Create test spore
    spore_graph.add((test_spore_uri, RDF.type, TEST.Spore))
    
    # Create SporeIntegrator instance
    integrator = SporeIntegrator(test_data_dir)
    
    # Mock validator's graph and guidance graph
    integrator.validator.graph = spore_graph
    integrator.validator.guidance_graph = guidance_graph
    integrator.spore_uri = test_spore_uri
    
    # Add conformance levels to guidance graph
    for level_str, level_uri in CONFORMANCE_LEVELS.items():
        guidance_graph.add((level_uri, RDF.type, GUIDANCE.ConformanceLevel))
    
    return integrator

@pytest.mark.parallel
def test_namespace_validation_strict(integrator: SporeIntegrator) -> None:
    """Test namespace validation in STRICT mode."""
    logger.info("Testing namespace validation in STRICT mode")
    try:
        integrator.set_conformance_level(GUIDANCE.STRICT)
        with pytest.raises(ConformanceError):
            integrator.validate_namespaces(integrator.spore_uri)
        logger.info("Namespace validation test passed")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

@pytest.mark.parallel
def test_namespace_validation_invalid(integrator: SporeIntegrator) -> None:
    """Test namespace validation with invalid namespace."""
    # Set strict conformance
    integrator.set_conformance_level("STRICT")
    
    # Add invalid namespace usage
    invalid_ns = Namespace("http://example.org/invalid# ")
    integrator.validator.graph.add((integrator.spore_uri, invalid_ns.hasProperty, TEST.SomeValue))
    
    # Validation should fail
    with pytest.raises(ConformanceError):
        integrator.validate_namespaces(integrator.spore_uri)

@pytest.mark.parallel
def test_namespace_validation_relaxed(integrator: SporeIntegrator) -> None:
    """Test namespace validation in RELAXED mode."""
    logger.info("Testing namespace validation in RELAXED mode")
    try:
        integrator.set_conformance_level(GUIDANCE.RELAXED)
        result = integrator.validate_namespaces(integrator.spore_uri)
        assert result is True
        logger.info("Namespace validation test passed")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

@pytest.mark.parallel
def test_prefix_validation_strict(integrator: SporeIntegrator) -> None:
    """Test prefix validation in STRICT mode."""
    logger.info("Testing prefix validation in STRICT mode")
    try:
        integrator.set_conformance_level(GUIDANCE.STRICT)
        with pytest.raises(ConformanceError):
            integrator.validate_prefixes(integrator.spore_uri)
        logger.info("Prefix validation test passed")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

@pytest.mark.parallel
def test_prefix_validation_invalid(integrator: SporeIntegrator) -> None:
    """Test prefix validation with invalid prefix."""
    # Set strict conformance
    integrator.set_conformance_level("STRICT")
    
    # Add invalid prefix usage
    invalid_ns = Namespace("http://example.org/invalid# ")
    integrator.validator.graph.add((integrator.spore_uri, invalid_ns.hasProperty, TEST.SomeValue))
    
    # Validation should fail
    with pytest.raises(ConformanceError):
        integrator.validate_prefixes(integrator.spore_uri)

@pytest.mark.parallel
def test_prefix_validation_relaxed(integrator: SporeIntegrator) -> None:
    """Test prefix validation in RELAXED mode."""
    logger.info("Testing prefix validation in RELAXED mode")
    try:
        integrator.set_conformance_level(GUIDANCE.RELAXED)
        result = integrator.validate_prefixes(integrator.spore_uri)
        assert result is True
        logger.info("Prefix validation test passed")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

@pytest.mark.parallel
def test_resolve_conformance_level(integrator: SporeIntegrator) -> None:
    """Test the resolution of conformance levels from different input types."""
    logger.info("Starting test_resolve_conformance_level")
    
    # Test string input
    string_level: str = "MODERATE"
    string_check: URIRef = GUIDANCE.STRICT
    uri_check: Optional[URIRef] = None
    result = integrator._resolve_conformance_level(string_level, string_check, uri_check)
    assert result == string_check
    logger.info("String input test passed")
    
    # Test URIRef input
    uri_level: URIRef = GUIDANCE.MODERATE
    string_check = None
    uri_check = uri_level
    result = integrator._resolve_conformance_level(uri_level, string_check, uri_check)
    assert result == uri_check
    logger.info("URIRef input test passed")
    
    logger.info("test_resolve_conformance_level completed successfully")
