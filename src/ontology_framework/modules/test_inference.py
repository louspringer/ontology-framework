"""Module for inferring test targets from orphaned tests."""

import ast
import importlib
import inspect
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)

class TestTargetInferrer(ast.NodeVisitor):
    """Analyzes test files to infer potential test targets based on code patterns."""
    
    def __init__(self, test_file: Path, src_path: Path):
        """Initialize the test target inferrer.
        
        Args:
            test_file: Path to the test file to analyze
            src_path: Path to the source directory
        """
        self.test_file = test_file
        self.src_path = src_path
        
        # Add source directory to Python path if not already there
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        self.imports: Dict[str, str] = {}  # module_name -> imported_name
        self.class_cache: Dict[str, Set[str]] = {}  # module_name -> {class_name: methods}
        self.current_test = ""
        self.test_functions: List[str] = []  # List of test function names
        self.potential_targets: Dict[str, Dict[str, float]] = {}  # test_name -> {target: confidence}
        self.visited_names: Set[str] = set()  # Track visited names to avoid duplicate confidence assignments
        
    def _get_module_classes(self, module_path: str) -> Set[str]:
        """Get all classes defined in a module."""
        try:
            module = importlib.import_module(module_path)
            return {
                name for name, obj in inspect.getmembers(module)
                if inspect.isclass(obj) and obj.__module__ == module_path
            }
        except Exception as e:
            logger.debug(f"Error getting classes for {module_path}: {e}")
            return set()
            
    def _get_class_methods(self, class_name: str, module_path: str) -> Set[str]:
        """Get all methods defined in a class."""
        cache_key = f"{module_path}.{class_name}"
        if cache_key in self.class_cache:
            return self.class_cache[cache_key]
            
        try:
            module = importlib.import_module(module_path)
            class_obj = getattr(module, class_name)
            methods = {
                name for name, obj in inspect.getmembers(class_obj)
                if inspect.isfunction(obj) or inspect.ismethod(obj)
            }
            self.class_cache[cache_key] = methods
            return methods
        except Exception as e:
            logger.debug(f"Error getting methods for {class_name}: {e}")
            return set()
            
    def visit_Import(self, node: ast.Import) -> None:
        """Process import statements."""
        for name in node.names:
            self.imports[name.asname or name.name] = name.name
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Process from-import statements."""
        module = node.module or ""
        for name in node.names:
            imported_name = name.asname or name.name
            self.imports[imported_name] = f"{module}.{name.name}"
        self.generic_visit(node)
        
    def visit_FunctionDef(self, node):
        """Process function definitions to identify test functions."""
        if node.name.startswith("test_"):
            self.current_test = node.name
            self.test_functions.append(node.name)
            self.potential_targets[node.name] = {}
            
            # Check return type hint
            if node.returns:
                if isinstance(node.returns, ast.Name):
                    target = node.returns.id
                    self._add_target_confidence(target, 0.9)  # Highest confidence for type hints
                elif isinstance(node.returns, ast.Attribute):
                    target = f"{node.returns.value.id}.{node.returns.attr}"
                    self._add_target_confidence(target, 0.9)

            # Check argument type hints
            for arg in node.args.args:
                if arg.annotation:
                    if isinstance(arg.annotation, ast.Name):
                        target = arg.annotation.id
                        self._add_target_confidence(target, 0.9)
                    elif isinstance(arg.annotation, ast.Attribute):
                        target = f"{arg.annotation.value.id}.{arg.annotation.attr}"
                        self._add_target_confidence(target, 0.9)

        self.generic_visit(node)
        
    def visit_Call(self, node):
        """Process function/method calls to identify potential test targets."""
        if self.current_test:
            if isinstance(node.func, ast.Attribute):
                # Handle method calls like obj.method()
                if isinstance(node.func.value, ast.Name):
                    obj_name = node.func.value.id
                    method_name = node.func.attr
                    # Add both class and method level targets
                    if obj_name in self.imports:
                        class_name = self.imports[obj_name].split('.')[-1]  # Get the class name from import
                        self._add_target_confidence(class_name, 0.6)  # Add class target
                        self._add_target_confidence(f"{class_name}.{method_name}", 0.8)  # Add method target
        self.generic_visit(node)
        
    def visit_Assert(self, node):
        """Process assertions to identify potential test targets."""
        if self.current_test:
            # Handle assertions involving class methods
            if isinstance(node.test, ast.Call) and isinstance(node.test.func, ast.Attribute):
                if isinstance(node.test.func.value, ast.Name):
                    obj_name = node.test.func.value.id
                    method_name = node.test.func.attr
                    if obj_name in self.imports:
                        class_name = self.imports[obj_name].split('.')[-1]  # Get the class name from import
                        self._add_target_confidence(class_name, 0.6)  # Add class target
                        self._add_target_confidence(f"{class_name}.{method_name}", 0.7)  # Add method target
        self.generic_visit(node)
        
    def visit_Assign(self, node):
        """Visit assignments to analyze test dependencies."""
        if not self.current_test:  # Check for empty string
            return
            
        # Check assignments for dependencies
        if isinstance(node.value, ast.Call):
            self.visit(node.value)
            
        # Check for type hints in assignments
        for target in node.targets:
            if isinstance(target, ast.Name) and hasattr(target, 'annotation'):
                if isinstance(target.annotation, ast.Name):
                    class_name = target.annotation.id
                    if class_name in self.imports:
                        impl_path = self.imports[class_name]
                        if impl_path.startswith("src.ontology_framework"):
                            self._add_target_confidence(class_name, 0.6)  # Medium confidence for variable types
                            
                            # Check if this is a class from our codebase
                            module_path = ".".join(impl_path.split(".")[:-1])
                            if class_name in self._get_module_classes(module_path):
                                # Add all methods of the class as potential dependencies
                                methods = self._get_class_methods(class_name, module_path)
                                for method in methods:
                                    self._add_target_confidence(f"{class_name}.{method}", 0.5)  # Lower confidence for method references
                                    
    def visit_Name(self, node):
        """Visit name nodes to track class usage."""
        if not self.current_test:  # Check for empty string
            return
        if node.id in self.imports and node.id not in self.visited_names:
            impl_path = self.imports[node.id]
            if impl_path.startswith("src.ontology_framework"):
                self._add_target_confidence(impl_path.split(".")[-1], 0.6)  # Medium confidence for class usage
                self.visited_names.add(node.id)
                
    def _add_target_confidence(self, target: str, confidence: float):
        """Add a potential target with a confidence score."""
        if self.current_test:
            current_confidence = self.potential_targets[self.current_test].get(target, 0.0)
            self.potential_targets[self.current_test][target] = max(current_confidence, confidence)

def infer_test_targets(test_file: Union[str, Path], src_path: Union[str, Path]) -> Dict[str, Dict[str, float]]:
    """Analyze a test file to infer its potential test targets.
    
    Args:
        test_file: Path to the test file to analyze
        src_path: Path to the source directory
        
    Returns:
        A dictionary mapping test function names to their potential targets and confidence scores
    """
    with open(test_file, 'r') as f:
        tree = ast.parse(f.read())
        
    inferrer = TestTargetInferrer(Path(test_file), Path(src_path))
    inferrer.visit(tree)
    return inferrer.potential_targets
