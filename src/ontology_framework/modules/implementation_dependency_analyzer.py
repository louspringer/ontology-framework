"""Module for analyzing implementation dependencies with internal firewalls."""

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

class ImplementationDependencyAnalyzer:
    """Analyzes dependencies within implementation code."""
    
    def __init__(self, src_path: Path):
        self.src_path = src_path
        self.dependency_graph = nx.DiGraph()
        self.module_cache = {}
        self.class_cache = {}
        
    def analyze_module_dependencies(self) -> Dict[str, Set[str]]:
        """Analyze module-level dependencies with internal firewall."""
        module_deps = {}
        
        # Track imports between modules
        for py_file in self.src_path.rglob("*.py"):
            with open(py_file, 'r') as f:
                tree = ast.parse(f.read())
                
            module_name = self._get_module_name(py_file)
            if module_name not in module_deps:
                module_deps[module_name] = set()
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        dep_module = name.name.split('.')[0]
                        module_deps[module_name].add(dep_module)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dep_module = node.module.split('.')[0]
                        module_deps[module_name].add(dep_module)
                        
        return module_deps
        
    def analyze_class_dependencies(self) -> Dict[str, Set[str]]:
        """Analyze class-level dependencies with internal firewall."""
        class_deps = {}
        
        # Track inheritance and composition
        for py_file in self.src_path.rglob("*.py"):
            with open(py_file, 'r') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    if class_name not in class_deps:
                        class_deps[class_name] = set()
                        
                    # Track inheritance
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            class_deps[class_name].add(base.id)
                            
                    # Track composition
                    for stmt in node.body:
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Name):
                                    if isinstance(stmt.value, ast.Call):
                                        if isinstance(stmt.value.func, ast.Name):
                                            class_deps[class_name].add(stmt.value.func.id)
                                            
        return class_deps
        
    def analyze_method_dependencies(self) -> Dict[str, Set[str]]:
        """Analyze method-level dependencies."""
        method_deps = {}
        current_class = None
        
        for file_path in self.src_path.rglob("*.py"):
            if file_path.name.startswith("__"):
                continue
                
            with open(file_path, "r") as f:
                tree = ast.parse(f.read())
                
            current_method = None
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    current_class = node.name
                elif isinstance(node, ast.FunctionDef):
                    current_method = f"{current_class}.{node.name}" if current_class else node.name
                    if current_method not in method_deps:
                        method_deps[current_method] = set()
                        
                elif isinstance(node, ast.Call):
                    if current_method:
                        if isinstance(node.func, ast.Attribute):
                            # Handle different types of value nodes
                            if isinstance(node.func.value, ast.Name):
                                method_deps[current_method].add(f"{node.func.value.id}.{node.func.attr}")
                            elif isinstance(node.func.value, ast.Attribute):
                                # Handle nested attributes (e.g., self.something.method())
                                value = node.func.value
                                while isinstance(value, ast.Attribute):
                                    value = value.value
                                if isinstance(value, ast.Name):
                                    method_deps[current_method].add(f"{value.id}.{node.func.attr}")
                        elif isinstance(node.func, ast.Name):
                            method_deps[current_method].add(node.func.id)
                            
        return method_deps
        
    def build_dependency_graph(self) -> nx.DiGraph:
        """Build complete dependency graph from all analyses."""
        # Combine all dependency analyses
        module_deps = self.analyze_module_dependencies()
        class_deps = self.analyze_class_dependencies()
        method_deps = self.analyze_method_dependencies()
        
        # Build graph
        for source, targets in module_deps.items():
            for target in targets:
                self.dependency_graph.add_edge(source, target, type='module')
                
        for source, targets in class_deps.items():
            for target in targets:
                self.dependency_graph.add_edge(source, target, type='class')
                
        for source, targets in method_deps.items():
            for target in targets:
                self.dependency_graph.add_edge(source, target, type='method')
                
        return self.dependency_graph
        
    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        relative_path = file_path.relative_to(self.src_path)
        return '.'.join(relative_path.with_suffix('').parts) 