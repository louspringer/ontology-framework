"""Module for analyzing and validating test coverage."""

import ast
import importlib
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import logging
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
TEST = Namespace("http://example.org/test#")
IMPL = Namespace("http://example.org/implementation#")
BASE = Namespace("http://example.org/ontology-framework#")
GUIDANCE = Namespace("http://example.org/guidance#")
VALIDATION = Namespace("http://example.org/validation#")

class TestCoverageAnalyzer:
    """Analyzes and validates test coverage for Python modules."""
    
    def __init__(self, src_path: Optional[Path] = None, test_path: Optional[Path] = None):
        """Initialize the test coverage analyzer.
        
        Args:
            src_path: Path to source directory
            test_path: Path to test directory
        """
        self.src_path = src_path or Path(__file__).parent.parent.parent
        self.test_path = test_path or self.src_path.parent / "tests"
        
        # Add paths to Python path if not already there
        for path in [str(self.src_path), str(self.test_path)]:
            if path not in sys.path:
                sys.path.insert(0, path)
        
        self.coverage_graph = Graph()
        self.coverage_graph.bind("test", TEST)
        self.coverage_graph.bind("impl", IMPL)
        self.coverage_graph.bind("of", BASE)
        self.coverage_graph.bind("guidance", GUIDANCE)
        self.coverage_graph.bind("validation", VALIDATION)
        
        # Initialize with base triples
        self.coverage_graph.add((TEST.TestCoverage, RDF.type, RDFS.Class))
        self.coverage_graph.add((TEST.TestCoverage, RDFS.label, Literal("Test Coverage")))
        self.coverage_graph.add((TEST.hasTest, RDF.type, RDF.Property))
        self.coverage_graph.add((TEST.hasTest, RDFS.domain, TEST.TestCoverage))
        self.coverage_graph.add((TEST.hasTest, RDFS.range, TEST.Test))

    def analyze_source_files(self, directory: Optional[Path] = None) -> Dict[str, Set[str]]:
        """Analyze Python source files to identify implementation components.
        
        Args:
            directory: Directory to analyze, defaults to src_path
            
        Returns:
            Dictionary mapping component names to sets of method names
        """
        directory = directory or self.src_path
        components: Dict[str, Set[str]] = {}
        
        for file_path in directory.rglob("*.py"):
            if file_path.name.startswith("test_"):
                continue
                
            try:
                module_path = str(file_path.relative_to(self.src_path.parent)).replace("/", ".")
                module_name = module_path.replace(".py", "")
                
                # Import the module
                module = importlib.import_module(module_name)
                
                # Analyze classes and methods
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj):
                        class_name = f"{module_name}.{name}"
                        components[class_name] = set()
                        
                        for method_name, method in inspect.getmembers(obj):
                            if inspect.isfunction(method) and not method_name.startswith("_"):
                                components[class_name].add(method_name)
                                
                                # Add to coverage graph
                                component_uri = URIRef(f"{IMPL}{class_name}")
                                method_uri = URIRef(f"{IMPL}{class_name}.{method_name}")
                                
                                self.coverage_graph.add((component_uri, RDF.type, IMPL.Component))
                                self.coverage_graph.add((method_uri, RDF.type, IMPL.Method))
                                self.coverage_graph.add((component_uri, IMPL.hasMethod, method_uri))
                
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")
                
        return components

    def analyze_test_files(self, directory: Optional[Path] = None) -> Dict[str, Set[str]]:
        """Analyze test files to determine test coverage.
        
        Args:
            directory: Directory to analyze, defaults to test_path
            
        Returns:
            Dictionary mapping test names to sets of tested components
        """
        directory = directory or self.test_path
        coverage: Dict[str, Set[str]] = {}
        
        for file_path in directory.rglob("test_*.py"):
            try:
                with open(file_path) as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                        coverage[node.name] = set()
                        
                        # Look for imports and class references
                        for child in ast.walk(node):
                            if isinstance(child, ast.Name):
                                component_name = child.id
                                if component_name in sys.modules:
                                    coverage[node.name].add(component_name)
                            elif isinstance(child, ast.Attribute):
                                # Handle dotted names (e.g., module.class.method)
                                full_name = []
                                current = child
                                while isinstance(current, ast.Attribute):
                                    full_name.insert(0, current.attr)
                                    current = current.value
                                if isinstance(current, ast.Name):
                                    full_name.insert(0, current.id)
                                    component_name = ".".join(full_name)
                                    coverage[node.name].add(component_name)
                                    
                                    # Add to coverage graph
                                    test_uri = URIRef(f"{TEST}{node.name}")
                                    component_uri = URIRef(f"{IMPL}{component_name}")
                                    
                                    self.coverage_graph.add((test_uri, RDF.type, TEST.Test))
                                    self.coverage_graph.add((test_uri, TEST.tests, component_uri))
                
            except Exception as e:
                logger.warning(f"Error analyzing {file_path}: {e}")
                
        return coverage

    def validate_coverage(self, guidance_graph: Optional[Graph] = None) -> bool:
        """Validate test coverage against requirements.
        
        Args:
            guidance_graph: Optional guidance graph with coverage requirements
            
        Returns:
            True if coverage meets requirements, False otherwise
        """
        if guidance_graph:
            requirements = self._get_coverage_requirements(guidance_graph)
            coverage_graph = self._generate_coverage_graph()
            
            for component, required_coverage in requirements.items():
                actual_coverage = self._calculate_coverage(component, coverage_graph)
                if actual_coverage < required_coverage:
                    logger.warning(
                        f"Insufficient coverage for {component}: "
                        f"required {required_coverage}%, actual {actual_coverage}%"
                    )
                    return False
        return True

    def _get_coverage_requirements(self, guidance_graph: Graph) -> Dict[str, float]:
        """Get coverage requirements from guidance graph.
        
        Args:
            guidance_graph: Guidance graph with coverage requirements
            
        Returns:
            Dictionary mapping component names to required coverage percentages
        """
        requirements = {}
        query = """
            SELECT ?component ?coverage
            WHERE {
                ?component a guidance:Component ;
                          guidance:requiredCoverage ?coverage .
            }
        """
        
        for row in guidance_graph.query(query):
            component = str(row.component)
            coverage = float(row.coverage)
            requirements[component] = coverage
            
        return requirements

    def _calculate_coverage(self, component: str, coverage_graph: Graph) -> float:
        """Calculate actual test coverage for a component.
        
        Args:
            component: Component name
            coverage_graph: Graph with coverage information
            
        Returns:
            Coverage percentage
        """
        total_methods = 0
        covered_methods = 0
        
        query = """
            SELECT ?method
            WHERE {
                ?component impl:hasMethod ?method .
            }
        """
        
        component_uri = URIRef(f"{IMPL}{component}")
        for row in coverage_graph.query(query, initBindings={"component": component_uri}):
            total_methods += 1
            method = str(row.method)
            
            # Check if method is tested
            if (None, TEST.tests, URIRef(method)) in coverage_graph:
                covered_methods += 1
                
        return (covered_methods / total_methods * 100) if total_methods > 0 else 0

    def generate_report(self) -> str:
        """Generate a human-readable coverage report.
        
        Returns:
            Report string
        """
        report = ["Test Coverage Report", "==================="]
        
        # Query for components and their methods
        query = """
            SELECT ?component ?method
            WHERE {
                ?component a impl:Component ;
                          impl:hasMethod ?method .
            }
        """
        
        current_component = None
        for row in self.coverage_graph.query(query):
            component = str(row.component).split("#")[-1]
            method = str(row.method).split("#")[-1]
            
            if component != current_component:
                report.append(f"\nComponent: {component}")
                current_component = component
                
            # Check if method is tested
            test_query = f"""
                SELECT ?test
                WHERE {{
                    ?test a test:Test ;
                          test:tests <{row.method}> .
                }}
            """
            
            tests = list(self.coverage_graph.query(test_query))
            status = "✓" if tests else "✗"
            report.append(f"  {status} {method}")
            
            if tests:
                for test in tests:
                    test_name = str(test[0]).split("#")[-1]
                    report.append(f"    - {test_name}")
                    
        return "\n".join(report) 