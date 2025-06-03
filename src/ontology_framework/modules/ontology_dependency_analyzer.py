# !/usr/bin/env python3
"""Module for analyzing ontology dependencies with internal firewalls."""

from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
import networkx as nx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OntologyDependencyAnalyzer:
    """Analyzes dependencies within and between ontologies."""
    
    def __init__(self, ontology_path: Path):
        self.ontology_path = ontology_path
        self.graph = Graph()
        self.dependency_graph = nx.DiGraph()
        self._load_ontology()
        
    def _load_ontology(self):
        """Load ontology file with error handling."""
        try:
            self.graph.parse(str(self.ontology_path), format='turtle')
        except Exception as e:
            logger.error(f"Error loading ontology: {e}")
            raise
            
    def analyze_namespace_dependencies(self) -> Dict[str, Set[str]]:
        """Analyze namespace dependencies with internal firewall."""
        namespace_deps = {}
        
        # Internal namespace tracking
        namespaces = set()
        for prefix, uri in self.graph.namespaces():
            namespaces.add(f"{prefix}:{uri}")
            
        # Track imports and references
        for s, p, o in self.graph:
            if p == OWL.imports:
                source = str(s)
                target = str(o)
                if source not in namespace_deps:
                    namespace_deps[source] = set()
                namespace_deps[source].add(target)
                
        return namespace_deps
        
    def analyze_class_dependencies(self) -> Dict[str, Set[str]]:
        """Analyze class hierarchy dependencies with internal firewall."""
        class_deps = {}
        
        # Track subclass relationships
        for s, p, o in self.graph:
            if p == RDFS.subClassOf:
                subclass = str(s)
                superclass = str(o)
                if subclass not in class_deps:
                    class_deps[subclass] = set()
                class_deps[subclass].add(superclass)
                
        return class_deps
        
    def analyze_property_dependencies(self) -> Dict[str, Set[str]]:
        """Analyze property dependencies with internal firewall."""
        property_deps = {}
        
        # Track domain/range relationships
        for s, p, o in self.graph:
            if p in [RDFS.domain, RDFS.range]:
                property_uri = str(s)
                class_uri = str(o)
                if property_uri not in property_deps:
                    property_deps[property_uri] = set()
                property_deps[property_uri].add(class_uri)
                
        return property_deps
        
    def analyze_constraint_dependencies(self) -> Dict[str, Set[str]]:
        """Analyze SHACL constraint dependencies with internal firewall."""
        constraint_deps = {}
        
        # Track constraint relationships
        for s, p, o in self.graph:
            if p == SH.targetClass:
                constraint = str(s)
                target = str(o)
                if constraint not in constraint_deps:
                    constraint_deps[constraint] = set()
                constraint_deps[constraint].add(target)
                
        return constraint_deps
        
    def build_dependency_graph(self) -> nx.DiGraph:
        """Build complete dependency graph from all analyses."""
        # Combine all dependency analyses
        namespace_deps = self.analyze_namespace_dependencies()
        class_deps = self.analyze_class_dependencies()
        property_deps = self.analyze_property_dependencies()
        constraint_deps = self.analyze_constraint_dependencies()
        
        # Build graph
        for source, targets in namespace_deps.items():
            for target in targets:
                self.dependency_graph.add_edge(source, target, type='namespace')
                
        for source, targets in class_deps.items():
            for target in targets:
                self.dependency_graph.add_edge(source, target, type='class')
                
        for source, targets in property_deps.items():
            for target in targets:
                self.dependency_graph.add_edge(source, target, type='property')
                
        for source, targets in constraint_deps.items():
            for target in targets:
                self.dependency_graph.add_edge(source, target, type='constraint')
                
        return self.dependency_graph 