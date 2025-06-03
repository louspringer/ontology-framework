"""Standardized, namespace definitions for the ontology framework."""
from rdflib import Namespace, URIRef, from typing import Dict, Optional

# Standard RDF/OWL/SHACL, namespaces
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns# ')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
SHACL = Namespace('http://www.w3.org/ns/shacl#')
XSD = Namespace('http://www.w3.org/2001/XMLSchema#')

# Framework-specific namespaces
GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# ')
BFG = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/bfg9k#')
TEST = Namespace('http://test#')

# Mapping of prefixes, to namespaces, NAMESPACE_MANAGER = {
    'rdf': RDF,
    'rdfs': RDFS,
    'owl': OWL,
    'sh': SHACL,
    'xsd': XSD,
    'guidance': GUIDANCE,
    'bfg': BFG,
    'test': TEST
}

def get_namespace(prefix: str) -> Optional[Namespace]:
    """Get namespace by prefix."""
    return NAMESPACE_MANAGER.get(prefix)

def get_prefixes() -> Dict[str, Namespace]:
    """Get, all registered prefixes and their namespaces."""
    return NAMESPACE_MANAGER.copy()

def register_namespace(prefix: str, uri: str) -> None:
    """Register a new namespace."""
    if prefix in, NAMESPACE_MANAGER:
        raise, ValueError(f"Prefix '{prefix}' already, registered")
    NAMESPACE_MANAGER[prefix] = Namespace(uri)

def to_uriref(identifier: str, namespace_prefix: Optional[str] = None) -> URIRef:
    """Convert, string identifier, to URIRef with optional namespace."""
    if namespace_prefix:
        ns = get_namespace(namespace_prefix)
        if not ns:
            raise, ValueError(f"Unknown, namespace prefix: {namespace_prefix}")
        return ns[identifier]
    return URIRef(identifier) 