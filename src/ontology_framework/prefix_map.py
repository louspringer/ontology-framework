"""Prefix map module for managing ontology prefixes."""

from enum import Enum
from rdflib import Graph, Namespace
from typing import Dict, Optional


class PrefixCategory(Enum):
    """Categories for prefixes."""
    STANDARD = "standard"      # RDF, RDFS, OWL, etc.
    DOMAIN = "domain"         # Domain-specific ontologies
    EXTERNAL = "external"     # External ontologies
    LOCAL = "local"          # Local project ontologies


class PrefixMap:
    """Manages ontology prefixes and their mappings."""
    
    def __init__(self):
        self.prefixes: Dict[str, str] = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'dct': 'http://purl.org/dc/terms/',
            'meta': 'http://ontologies.louspringer.com/meta#',
            'guidance': 'http://ontologies.louspringer.com/guidance#',
            'problem': 'http://ontologies.louspringer.com/problem#',
            'solution': 'http://ontologies.louspringer.com/solution#',
            'conversation': 'http://ontologies.louspringer.com/conversation#',
            'process': 'http://ontologies.louspringer.com/process#',
            'agent': 'http://ontologies.louspringer.com/agent#',
            'time': 'http://ontologies.louspringer.com/time#',
            'sh': 'http://www.w3.org/ns/shacl#'
        }
        
    def add_prefix(self, prefix: str, uri: str) -> None:
        """Add a new prefix mapping."""
        self.prefixes[prefix] = uri
        
    def get_uri(self, prefix: str) -> Optional[str]:
        """Get the URI for a prefix."""
        return self.prefixes.get(prefix)
        
    def get_namespace(self, prefix: str) -> Optional[str]:
        """Get the namespace URI for a prefix."""
        uri = self.get_uri(prefix)
        if uri:
            return Namespace(uri)
        return None
        
    def bind_to_graph(self, graph: Graph) -> None:
        """Bind all prefixes to a graph."""
        for prefix, uri in self.prefixes.items():
            graph.bind(prefix, Namespace(uri))
            
    def transform_uri(self, uri_str: str) -> str:
        """Transform URIs to use ontologies.louspringer.com domain consistently."""
        if uri_str.startswith('file:///'):
            # Extract the last part of the path after ontology-framework/
            parts = uri_str.split('ontology-framework/')
            if len(parts) > 1:
                return f'http://ontologies.louspringer.com/{parts[1]}'
            return uri_str
        elif uri_str.startswith('./'):
            # Handle relative URIs
            return f'http://ontologies.louspringer.com/{uri_str[2:]}'
        elif uri_str.startswith('http://example.org/') or uri_str.startswith('http://louspringer.com/'):
            # Replace example.org or louspringer.com with ontologies.louspringer.com
            return uri_str.replace(
                uri_str.split('/')[2], 
                'ontologies.louspringer.com'
            )
        return uri_str

# Create a default instance
default_prefix_map = PrefixMap() 