"""Module for analyzing test coverage dependencies with internal firewalls."""

import ast
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging
import networkx as nx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCoverageDependencyAnalyzer:
    """Analyzes dependencies between tests and implementation."""
    
    def __init__(self, test_path: Path, src_path: Path):
        self.test_path = test_path
        self.src_path = src_path
        self.dependency_graph = nx.DiGraph()
        self.imports = {}
        self.class_cache = {}
        
    def analyze_test_imports(self) -> Dict[str, Set[str]]:
        """Analyze test imports with internal firewall."""
        test_imports = {}
        
        # Track imports in test files
        for test_file in self.test_path.rglob("test_*.py"):
            with open(test_file, 'r') as f:
                tree = ast.parse(f.read())
                
            test_name = test_file.stem
            if test_name not in test_imports:
                test_imports[test_name] = set()
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        test_imports[test_name].add(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for name in node.names:
                            test_imports[test_name].add(f"{node.module}.{name.name}")
                            
        return test_imports
        
    def analyze_test_targets(self) -> Dict[str, Set[str]]:
        """Analyze test targets with internal firewall."""
        test_targets = {}
        
        # Track what each test is testing
        for test_file in self.test_path.rglob("test_*.py"):
            with open(test_file, 'r') as f:
                tree = ast.parse(f.read())
                
            current_test = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    current_test = node.name
                    if current_test not in test_targets:
                        test_targets[current_test] = set()
                        
                elif current_test and isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        # Method call
                        if isinstance(node.func.value, ast.Name):
                            obj_name = node.func.value.id
                            method_name = node.func.attr
                            test_targets[current_test].add(f"{obj_name}.{method_name}")
                    elif isinstance(node.func, ast.Name):
                        # Function call
                        test_targets[current_test].add(node.func.id)
                        
        return test_targets
        
    def analyze_test_assertions(self) -> Dict[str, Set[str]]:
        """Analyze test assertions to identify tested methods."""
        test_assertions = {}
        
        for file_path in self.test_path.rglob("test_*.py"):
            with open(file_path, "r") as f:
                tree = ast.parse(f.read())
                
            current_test = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    current_test = node.name
                    if current_test not in test_assertions:
                        test_assertions[current_test] = set()
                        
                elif current_test and isinstance(node, ast.Assert):
                    # Extract the object being asserted
                    if isinstance(node.test, ast.Call):
                        if isinstance(node.test.func, ast.Attribute):
                            # Handle different types of value nodes
                            if isinstance(node.test.func.value, ast.Name):
                                obj_name = node.test.func.value.id
                                method_name = node.test.func.attr
                                test_assertions[current_test].add(f"{obj_name}.{method_name}")
                            elif isinstance(node.test.func.value, ast.Attribute):
                                # Handle nested attributes (e.g., self.something.method())
                                value = node.test.func.value
                                while isinstance(value, ast.Attribute):
                                    value = value.value
                                if isinstance(value, ast.Name):
                                    test_assertions[current_test].add(f"{value.id}.{node.test.func.attr}")
                        elif isinstance(node.test.func, ast.Name):
                            test_assertions[current_test].add(node.test.func.id)
                            
        return test_assertions
        
    def build_dependency_graph(self) -> nx.DiGraph:
        """Build complete dependency graph from all analyses."""
        # Combine all dependency analyses
        test_imports = self.analyze_test_imports()
        test_targets = self.analyze_test_targets()
        test_assertions = self.analyze_test_assertions()
        
        # Build graph
        for test, imports in test_imports.items():
            for imp in imports:
                self.dependency_graph.add_edge(test, imp, type='import')
                
        for test, targets in test_targets.items():
            for target in targets:
                self.dependency_graph.add_edge(test, target, type='target')
                
        for test, assertions in test_assertions.items():
            for assertion in assertions:
                self.dependency_graph.add_edge(test, assertion, type='assertion')
                
        return self.dependency_graph
