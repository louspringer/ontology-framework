"""Tests for prefix map functionality."""

import pytest
from rdflib import Graph, Namespace, URIRef

from ontology_framework.prefix_map import PrefixCategory, PrefixMap, default_prefix_map


def test_default_prefixes():
    """Test that default prefixes are correctly initialized."""
    assert default_prefix_map.is_valid_prefix("rdf")
    assert default_prefix_map.is_valid_prefix("rdfs")
    assert default_prefix_map.is_valid_prefix("owl")
    assert default_prefix_map.is_valid_prefix("meta")
    assert default_prefix_map.is_valid_prefix("guidance")


def test_prefix_categories():
    """Test that prefixes are assigned to correct categories."""
    assert default_prefix_map.get_category("rdf") == PrefixCategory.EXTERNAL
    assert default_prefix_map.get_category("meta") == PrefixCategory.CORE
    assert default_prefix_map.get_category("nonexistent") is None


def test_namespace_resolution():
    """Test that namespaces are correctly resolved."""
    meta_ns = default_prefix_map.get_namespace("meta")
    assert meta_ns is not None
    assert str(meta_ns) == "http://ontologies.louspringer.com/meta#"

    rdf_ns = default_prefix_map.get_namespace("rdf")
    assert rdf_ns is not None
    assert str(rdf_ns) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


def test_graph_binding():
    """Test that prefixes are correctly bound to RDF graphs."""
    g = Graph()
    default_prefix_map.bind_to_graph(g)
    
    # Check that core prefixes are bound
    assert str(g.namespace_manager.store.namespace("meta")) == "http://ontologies.louspringer.com/meta#"
    assert str(g.namespace_manager.store.namespace("rdf")) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


def test_custom_prefix_registration():
    """Test registering custom prefixes."""
    prefix_map = PrefixMap()
    prefix_map.register_prefix("test", "./test#", PrefixCategory.DOMAIN)
    
    assert prefix_map.is_valid_prefix("test")
    assert prefix_map.get_category("test") == PrefixCategory.DOMAIN
    assert str(prefix_map.get_namespace("test")) == "./test#"


def test_prefix_map_isolation():
    """Test that PrefixMap instances are isolated."""
    map1 = PrefixMap()
    map2 = PrefixMap()
    
    map1.register_prefix("custom", "./custom#", PrefixCategory.DOMAIN)
    assert map1.is_valid_prefix("custom")
    assert not map2.is_valid_prefix("custom")


def test_get_all_prefixes():
    """Test retrieving all registered prefixes."""
    prefixes = default_prefix_map.get_all_prefixes()
    
    # Check core prefixes are included
    assert "meta" in prefixes
    assert "rdf" in prefixes
    assert "owl" in prefixes
    
    # Verify it's a copy
    prefixes["test"] = Namespace("./test#")
    assert not default_prefix_map.is_valid_prefix("test") 