"""Module for analyzing patterns across dependency analyzers."""

from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging
import networkx as nx
from .ontology_dependency_analyzer import OntologyDependencyAnalyzer
from .implementation_dependency_analyzer import ImplementationDependencyAnalyzer
from .test_coverage_dependency_analyzer import TestCoverageDependencyAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DependencyPatternAnalyzer:
    """Analyzes patterns across different types of dependencies."""
    
    def __init__(self, ontology_path: Path, src_path: Path, test_path: Path):
        self.ontology_analyzer = OntologyDependencyAnalyzer(ontology_path)
        self.implementation_analyzer = ImplementationDependencyAnalyzer(src_path)
        self.test_analyzer = TestCoverageDependencyAnalyzer(test_path, src_path)
        
    def analyze_common_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """Analyze common patterns across dependency types."""
        patterns = {
            'hierarchical': [],
            'circular': [],
            'orphaned': [],
            'transitive': []
        }
        
        # Build all graphs
        ontology_graph = self.ontology_analyzer.build_dependency_graph()
        impl_graph = self.implementation_analyzer.build_dependency_graph()
        test_graph = self.test_analyzer.build_dependency_graph()
        
        # Analyze hierarchical patterns
        patterns['hierarchical'].extend(
            self._find_hierarchical_patterns(ontology_graph, 'ontology') +
            self._find_hierarchical_patterns(impl_graph, 'implementation') +
            self._find_hierarchical_patterns(test_graph, 'test')
        )
        
        # Analyze circular dependencies
        patterns['circular'].extend(
            self._find_circular_dependencies(ontology_graph, 'ontology') +
            self._find_circular_dependencies(impl_graph, 'implementation') +
            self._find_circular_dependencies(test_graph, 'test')
        )
        
        # Analyze orphaned components
        patterns['orphaned'].extend(
            self._find_orphaned_components(ontology_graph, 'ontology') +
            self._find_orphaned_components(impl_graph, 'implementation') +
            self._find_orphaned_components(test_graph, 'test')
        )
        
        # Analyze transitive dependencies
        patterns['transitive'].extend(
            self._find_transitive_dependencies(ontology_graph, 'ontology') +
            self._find_transitive_dependencies(impl_graph, 'implementation') +
            self._find_transitive_dependencies(test_graph, 'test')
        )
        
        return patterns
        
    def _find_hierarchical_patterns(self, graph: nx.DiGraph, graph_type: str) -> List[Tuple[str, str]]:
        """Find hierarchical dependency patterns."""
        patterns = []
        for node in graph.nodes():
            # Check for deep inheritance chains
            ancestors = nx.ancestors(graph, node)
            if len(ancestors) > 2:  # More than direct parent
                patterns.append((f"deep_hierarchy_{graph_type}", node))
                
            # Check for wide inheritance trees
            descendants = nx.descendants(graph, node)
            if len(descendants) > 3:  # More than a few children
                patterns.append((f"wide_hierarchy_{graph_type}", node))
                
        return patterns
        
    def _find_circular_dependencies(self, graph: nx.DiGraph, graph_type: str) -> List[Tuple[str, str]]:
        """Find circular dependency patterns."""
        patterns = []
        cycles = list(nx.simple_cycles(graph))
        for cycle in cycles:
            if len(cycle) > 2:  # Ignore simple mutual dependencies
                patterns.append((f"circular_{graph_type}", " -> ".join(cycle)))
        return patterns
        
    def _find_orphaned_components(self, graph: nx.DiGraph, graph_type: str) -> List[Tuple[str, str]]:
        """Find orphaned components."""
        patterns = []
        for node in graph.nodes():
            if not graph.in_edges(node) and not graph.out_edges(node):
                patterns.append((f"orphaned_{graph_type}", node))
        return patterns
        
    def _find_transitive_dependencies(self, graph: nx.DiGraph, graph_type: str) -> List[Tuple[str, str]]:
        """Find transitive dependency patterns."""
        patterns = []
        for node in graph.nodes():
            # Find nodes that are both direct and indirect dependencies
            direct_deps = set(graph.successors(node))
            indirect_deps = set()
            for dep in direct_deps:
                indirect_deps.update(nx.descendants(graph, dep))
                
            # If a node is both direct and indirect dependency
            transitive = direct_deps.intersection(indirect_deps)
            if transitive:
                patterns.append((f"transitive_{graph_type}", f"{node} -> {transitive}"))
                
        return patterns
        
    def compare_dependency_types(self) -> Dict[str, Dict[str, int]]:
        """Compare dependency types across graphs."""
        stats = {
            'ontology': self._get_dependency_stats(self.ontology_analyzer.build_dependency_graph()),
            'implementation': self._get_dependency_stats(self.implementation_analyzer.build_dependency_graph()),
            'test': self._get_dependency_stats(self.test_analyzer.build_dependency_graph())
        }
        return stats
        
    def _get_dependency_stats(self, graph: nx.DiGraph) -> Dict[str, int]:
        """Get statistics about dependency types in a graph."""
        stats = {
            'total_nodes': graph.number_of_nodes(),
            'total_edges': graph.number_of_edges(),
            'avg_in_degree': sum(dict(graph.in_degree()).values()) / graph.number_of_nodes(),
            'avg_out_degree': sum(dict(graph.out_degree()).values()) / graph.number_of_nodes(),
            'max_depth': self._calculate_max_depth(graph)
        }
        return stats
        
    def _calculate_max_depth(self, graph: nx.DiGraph) -> int:
        """Calculate maximum depth of dependency chain."""
        if not graph.nodes():
            return 0
            
        max_depth = 0
        for node in graph.nodes():
            depth = len(nx.shortest_path_length(graph, node))
            max_depth = max(max_depth, depth)
        return max_depth 