# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: [current version from guidance.ttl]
# Behavioral-Profile: ClaudeReflector

"""Module for analyzing ontology structure and relationships."""

from typing import List, Dict, Optional, Set, Tuple, Any, Union, cast
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
from pathlib import Path
from rdflib.term import Node
import logging

logger = logging.getLogger(__name__)

class OntologyAnalyzer:
    """Class for analyzing ontology structure and relationships."""
    
    def __init__(self, graph: Graph) -> None:
        """Initialize the analyzer.
        
        Args:
            graph: The RDF graph to analyze
        """
        self.graph = graph
        self._class_hierarchy: Optional[Dict[URIRef, Set[URIRef]]] = None
        self._property_hierarchy: Optional[Dict[URIRef, Set[URIRef]]] = None
        
    def get_all_classes(self) -> Set[URIRef]:
        """Get all classes in the ontology.
        
        Returns:
            Set of class URIs
        """
        classes = set()
        for s in self.graph.subjects(RDF.type, OWL.Class):
            if isinstance(s, URIRef):
                classes.add(s)
        return classes
        
    def get_all_properties(self) -> Set[URIRef]:
        """Get all properties in the ontology.
        
        Returns:
            Set of property URIs
        """
        properties = set()
        for s in self.graph.subjects(RDF.type, OWL.ObjectProperty):
            if isinstance(s, URIRef):
                properties.add(s)
        for s in self.graph.subjects(RDF.type, OWL.DatatypeProperty):
            if isinstance(s, URIRef):
                properties.add(s)
        return properties 