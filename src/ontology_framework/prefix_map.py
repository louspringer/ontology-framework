"""Prefix mapping functionality for the ontology framework.

This module provides functionality for managing ontology prefixes and namespaces,
including standard prefix mappings and prefix categorization.
"""

from typing import Dict, List, Optional, Set
from enum import Enum
import logging
from rdflib import Graph, Namespace, URIRef

logger = logging.getLogger(__name__)

class PrefixCategory(Enum):
    """Categories for prefix mappings."""
    CORE = "core"
    DOMAIN = "domain"
    EXTERNAL = "external"
    CUSTOM = "custom"

class PrefixMap:
    """Manages prefix mappings for ontologies."""
    
    def __init__(self):
        """Initialize prefix map."""
        self.prefixes: Dict[str, URIRef] = {}
        self.categories: Dict[str, PrefixCategory] = {}
        
    def add_prefix(self, prefix: str, uri: str, category: PrefixCategory) -> None:
        """Add a prefix mapping.
        
        Args:
            prefix: Prefix string
            uri: URI string
            category: Prefix category
        """
        self.prefixes[prefix] = URIRef(uri)
        self.categories[prefix] = category
        logger.info(f"Added prefix mapping: {prefix} -> {uri} ({category.value})")
        
    def remove_prefix(self, prefix: str) -> None:
        """Remove a prefix mapping.
        
        Args:
            prefix: Prefix to remove
        """
        if prefix in self.prefixes:
            del self.prefixes[prefix]
            del self.categories[prefix]
            logger.info(f"Removed prefix mapping: {prefix}")
            
    def get_uri(self, prefix: str) -> Optional[URIRef]:
        """Get URI for a prefix.
        
        Args:
            prefix: Prefix to look up
            
        Returns:
            URI if found, None otherwise
        """
        return self.prefixes.get(prefix)
        
    def get_category(self, prefix: str) -> Optional[PrefixCategory]:
        """Get category for a prefix.
        
        Args:
            prefix: Prefix to look up
            
        Returns:
            Category if found, None otherwise
        """
        return self.categories.get(prefix)
        
    def get_prefixes_by_category(self, category: PrefixCategory) -> Set[str]:
        """Get all prefixes in a category.
        
        Args:
            category: Category to filter by
            
        Returns:
            Set of prefixes in the category
        """
        return {prefix for prefix, cat in self.categories.items() if cat == category}
        
    def apply_to_graph(self, graph: Graph) -> None:
        """Apply prefix mappings to a graph.
        
        Args:
            graph: RDFlib Graph to apply mappings to
        """
        for prefix, uri in self.prefixes.items():
            graph.bind(prefix, Namespace(uri))
            
    def merge(self, other: 'PrefixMap') -> None:
        """Merge another prefix map into this one.
        
        Args:
            other: PrefixMap to merge
        """
        self.prefixes.update(other.prefixes)
        self.categories.update(other.categories)
        logger.info("Merged prefix mappings")

# Default prefix mappings
default_prefix_map = PrefixMap()

# Core prefixes
default_prefix_map.add_prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#", PrefixCategory.CORE)
default_prefix_map.add_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#", PrefixCategory.CORE)
default_prefix_map.add_prefix("owl", "http://www.w3.org/2002/07/owl#", PrefixCategory.CORE)
default_prefix_map.add_prefix("xsd", "http://www.w3.org/2001/XMLSchema#", PrefixCategory.CORE)

# Domain prefixes
default_prefix_map.add_prefix("skos", "http://www.w3.org/2004/02/skos/core#", PrefixCategory.DOMAIN)
default_prefix_map.add_prefix("dc", "http://purl.org/dc/elements/1.1/", PrefixCategory.DOMAIN)
default_prefix_map.add_prefix("dct", "http://purl.org/dc/terms/", PrefixCategory.DOMAIN)
default_prefix_map.add_prefix("foaf", "http://xmlns.com/foaf/0.1/", PrefixCategory.DOMAIN)

# External prefixes
default_prefix_map.add_prefix("schema", "http://schema.org/", PrefixCategory.EXTERNAL)
default_prefix_map.add_prefix("void", "http://rdfs.org/ns/void#", PrefixCategory.EXTERNAL)
default_prefix_map.add_prefix("prov", "http://www.w3.org/ns/prov#", PrefixCategory.EXTERNAL) 