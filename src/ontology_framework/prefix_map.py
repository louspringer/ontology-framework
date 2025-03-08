"""Prefix map module for managing ontology prefixes."""

from enum import Enum
from typing import Dict, Optional

from rdflib import Namespace


class PrefixCategory(Enum):
    """Categories of prefixes."""
    CORE = "core"
    DOMAIN = "domain"
    EXTERNAL = "external"


class PrefixMap:
    """Manages ontology prefixes and their mappings."""

    def __init__(self):
        """Initialize the prefix map with standard prefixes."""
        self._prefixes: Dict[str, Namespace] = {}
        self._categories: Dict[str, PrefixCategory] = {}
        
        # Initialize standard prefixes
        self.register_prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#", PrefixCategory.EXTERNAL)
        self.register_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#", PrefixCategory.EXTERNAL)
        self.register_prefix("owl", "http://www.w3.org/2002/07/owl#", PrefixCategory.EXTERNAL)
        self.register_prefix("xsd", "http://www.w3.org/2001/XMLSchema#", PrefixCategory.EXTERNAL)
        self.register_prefix("sh", "http://www.w3.org/ns/shacl#", PrefixCategory.EXTERNAL)
        
        # Core framework prefixes
        self.register_prefix("meta", "http://ontologies.louspringer.com/meta#", PrefixCategory.CORE)
        self.register_prefix("metameta", "http://ontologies.louspringer.com/metameta#", PrefixCategory.CORE)
        self.register_prefix("problem", "http://ontologies.louspringer.com/problem#", PrefixCategory.CORE)
        self.register_prefix("solution", "http://ontologies.louspringer.com/solution#", PrefixCategory.CORE)
        self.register_prefix("conversation", "http://ontologies.louspringer.com/conversation#", PrefixCategory.CORE)
        self.register_prefix("guidance", "http://ontologies.louspringer.com/guidance#", PrefixCategory.CORE)
        
    def register_prefix(self, prefix: str, uri: str, category: PrefixCategory) -> None:
        """Register a new prefix.
        
        Args:
            prefix: The prefix string (e.g., 'rdf')
            uri: The URI the prefix expands to
            category: The category of the prefix
        """
        self._prefixes[prefix] = Namespace(uri)
        self._categories[prefix] = category
        
    def get_namespace(self, prefix: str) -> Optional[Namespace]:
        """Get the namespace for a prefix.
        
        Args:
            prefix: The prefix to look up
            
        Returns:
            The namespace if found, None otherwise
        """
        return self._prefixes.get(prefix)
        
    def get_category(self, prefix: str) -> Optional[PrefixCategory]:
        """Get the category of a prefix.
        
        Args:
            prefix: The prefix to look up
            
        Returns:
            The category if found, None otherwise
        """
        return self._categories.get(prefix)
        
    def is_valid_prefix(self, prefix: str) -> bool:
        """Check if a prefix is valid.
        
        Args:
            prefix: The prefix to check
            
        Returns:
            True if the prefix is registered, False otherwise
        """
        return prefix in self._prefixes
        
    def get_all_prefixes(self) -> Dict[str, Namespace]:
        """Get all registered prefixes.
        
        Returns:
            Dictionary of prefix to namespace mappings
        """
        return self._prefixes.copy()
        
    def bind_to_graph(self, graph) -> None:
        """Bind all prefixes to an RDF graph.
        
        Args:
            graph: The RDFLib graph to bind prefixes to
        """
        for prefix, namespace in self._prefixes.items():
            graph.bind(prefix, namespace)


# Global instance for convenience
default_prefix_map = PrefixMap() 