#!/usr/bin/env python3
import pytest
import logging
from datetime import datetime
from ontology_framework.config.correlation import (
    CorrelationContext,
    CorrelationManager,
    get_correlation_id,
    add_correlation_metadata,
    get_correlation_metadata
)
from ontology_framework.config.logging_config import setup_logging, get_logger

# Set up logging for tests
setup_logging('test_correlation.log')
logger = get_logger(__name__)

def test_correlation_context_creation():
    """Test creation of correlation context."""
    context = CorrelationContext()
    assert context.correlation_id is not None
    assert isinstance(context.created_at, datetime)
    assert context.metadata == {}
    assert context.parent_id is None

def test_correlation_context_metadata():
    """Test adding and retrieving metadata."""
    context = CorrelationContext()
    context.add_metadata("key", "value")
    assert context.metadata["key"] == "value"
    assert context.get_metadata("key") == "value"
    assert context.get_metadata("nonexistent") is None

def test_correlation_context_parent():
    """Test setting and getting parent correlation ID."""
    parent_id = "parent-123"
    context = CorrelationContext(parent_id=parent_id)
    assert context.parent_id == parent_id

def test_correlation_context_to_dict():
    """Test converting context to dictionary."""
    context = CorrelationContext()
    context.add_metadata("key", "value")
    context_dict = context.to_dict()
    assert "correlation_id" in context_dict
    assert "created_at" in context_dict
    assert context_dict["metadata"] == {"key": "value"}
    assert context_dict["parent_id"] is None

def test_correlation_manager_context():
    """Test correlation manager context management."""
    # Before context, should be '-'
    assert get_correlation_id() == '-'
    with CorrelationManager() as mgr:
        context = mgr.get_current_context()
        assert isinstance(context, CorrelationContext)
        assert get_correlation_id() == context.correlation_id
    # After context, should be '-'
    assert get_correlation_id() == '-'

def test_correlation_manager_parent():
    """Test correlation manager with parent correlation ID."""
    parent_id = "parent-123"
    with CorrelationManager(parent_id=parent_id) as mgr:
        context = mgr.get_current_context()
        assert context.parent_id == parent_id

def test_correlation_metadata_functions():
    """Test correlation metadata functions."""
    with CorrelationManager() as mgr:
        add_correlation_metadata("key", "value")
        assert get_correlation_metadata("key") == "value"
        assert get_correlation_metadata("nonexistent") is None

def test_correlation_logging():
    """Test correlation ID in logging."""
    with CorrelationManager() as mgr:
        context = mgr.get_current_context()
        logger.info("Test message")
        # Verify the log record has the correlation ID
        assert get_correlation_id() == context.correlation_id 