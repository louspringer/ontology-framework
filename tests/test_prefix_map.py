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
    print("\n=== Testing Prefix Categories ===")
    
    # Log all available categories in the enum
    print("\nAvailable PrefixCategory values:")
    for category in PrefixCategory:
        print(f"- {category} (type: {type(category)}, value: {category.value}")
    
    # Test rdf prefix
    rdf_category = default_prefix_map.get_category("rdf")
    print(f"\nTesting 'rdf' prefix:")
    print(f"Category returned: {rdf_category}")
    print(f"Category type: {type(rdf_category)}")
    print(f"Category value: {rdf_category.value if rdf_category else None}")
    assert rdf_category.value == "external"
    
    # Test meta prefix
    meta_category = default_prefix_map.get_category("meta")
    print(f"\nTesting 'meta' prefix:")
    print(f"Category returned: {meta_category}")
    print(f"Category type: {type(meta_category)}")
    print(f"Category value: {meta_category.value if meta_category else None}")
    assert meta_category.value == "core"
    
    # Log all categories in the prefix map
    print("\nAll prefix categories in default_prefix_map:")
    for prefix, category in default_prefix_map.categories.items():
        print(f"{prefix}: {category} (type: {type(category)}, value: {category.value}")
    
    # Compare the actual category with CORE directly
    print("\nDirect comparison:")
    print(f"meta_category == PrefixCategory.CORE: {meta_category == PrefixCategory.CORE}")
    print(f"meta_category.value == PrefixCategory.CORE.value: {meta_category.value == PrefixCategory.CORE.value}")
    print(f"str(meta_category) == str(PrefixCategory.CORE): {str(meta_category) == str(PrefixCategory.CORE)}")
    
    assert meta_category == PrefixCategory.CORE


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