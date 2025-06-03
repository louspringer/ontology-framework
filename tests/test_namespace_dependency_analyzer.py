import unittest
from pathlib import Path
import networkx as nx
from rdflib import Graph, URIRef, Namespace
from scripts.namespace_dependency_analyzer import NamespaceDependencyAnalyzer

class TestNamespaceDependencyAnalyzer(unittest.TestCase):
    """Test cases for namespace dependency analyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = NamespaceDependencyAnalyzer()
        self.test_graph = Graph()
        
        # Set up test namespaces
        self.test_ns = Namespace("http://example.org/test#")
        self.dep_ns = Namespace("http://example.org/dependency#")
        
        # Add test data
        self.test_graph.add((
            self.test_ns.TestClass,
            URIRef("http://example.org/dependency#dependsOn"),
            self.dep_ns.DependencyClass
        ))

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(len(self.analyzer.get_dependencies()), 0)

    def test_analyze_dependencies(self):
        """Test dependency analysis."""
        dependencies = self.analyzer.analyze(self.test_graph)
        self.assertIsInstance(dependencies, nx.DiGraph)
        self.assertEqual(len(dependencies.nodes()), 2)
        self.assertEqual(len(dependencies.edges()), 1)

    def test_direct_dependencies(self):
        """Test direct dependency detection."""
        self.analyzer.analyze(self.test_graph)
        direct_deps = self.analyzer.get_direct_dependencies(str(self.test_ns))
        self.assertEqual(len(direct_deps), 1)
        self.assertIn(str(self.dep_ns), direct_deps)

    def test_transitive_dependencies(self):
        """Test transitive dependency detection."""
        # Add transitive dependency
        trans_ns = Namespace("http://example.org/transitive#")
        self.test_graph.add((
            self.dep_ns.DependencyClass,
            URIRef("http://example.org/dependency#dependsOn"),
            trans_ns.TransitiveClass
        ))
        
        self.analyzer.analyze(self.test_graph)
        trans_deps = self.analyzer.get_transitive_dependencies(str(self.test_ns))
        self.assertEqual(len(trans_deps), 2)
        self.assertIn(str(self.dep_ns), trans_deps)
        self.assertIn(str(trans_ns), trans_deps)

    def test_circular_dependencies(self):
        """Test circular dependency detection."""
        # Add circular dependency
        self.test_graph.add((
            self.dep_ns.DependencyClass,
            URIRef("http://example.org/dependency#dependsOn"),
            self.test_ns.TestClass
        ))
        
        self.analyzer.analyze(self.test_graph)
        circular_deps = self.analyzer.get_circular_dependencies()
        self.assertEqual(len(circular_deps), 1)
        self.assertEqual(len(circular_deps[0]), 2)

    def test_dependency_report(self):
        """Test dependency report generation."""
        self.analyzer.analyze(self.test_graph)
        report = self.analyzer.generate_report()
        
        self.assertIn("namespaces", report)
        self.assertIn("direct_dependencies", report)
        self.assertIn("transitive_dependencies", report)
        self.assertIn("circular_dependencies", report)

    def test_invalid_input(self):
        """Test invalid input handling."""
        with self.assertRaises(ValueError):
            self.analyzer.analyze("not a graph")

    def tearDown(self):
        """Clean up test fixtures."""
        self.analyzer = None
        self.test_graph = None
        self.test_ns = None
        self.dep_ns = None

if __name__ == '__main__':
    unittest.main() 