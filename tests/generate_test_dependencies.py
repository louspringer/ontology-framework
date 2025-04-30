"""Script to automatically generate test dependencies from test files."""

import ast
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import logging
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
TEST = Namespace("http://example.org/test#")
IMPL = Namespace("http://example.org/implementation#")
BASE = Namespace("http://example.org/ontology-framework#")

class TestDependencyAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze test dependencies."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.imports: Dict[str, str] = {}
        self.test_functions: List[str] = []
        self.dependencies: Dict[str, Set[Tuple[str, str]]] = {}
        self.current_test: Optional[str] = ""  # Initialize as empty string
        self.src_path = Path(__file__).parent.parent / "src" / "ontology_framework"
        self.module_cache: Dict[str, Set[str]] = {}
        self.class_cache: Dict[str, Set[str]] = {}
        
    def _get_module_classes(self, module_path: str) -> Set[str]:
        """Get all classes defined in a module."""
        if module_path in self.module_cache:
            return self.module_cache[module_path]
            
        try:
            module = importlib.import_module(module_path)
            classes = {
                name for name, obj in inspect.getmembers(module)
                if inspect.isclass(obj) and obj.__module__ == module_path
            }
            self.module_cache[module_path] = classes
            return classes
        except Exception as e:
            logger.debug(f"Error loading module {module_path}: {e}")
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
            
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname or alias.name
            self.imports[name] = alias.name
            
            # Try to find implementation classes
            if alias.name.startswith("src.ontology_framework"):
                self._get_module_classes(alias.name)
            
    def visit_ImportFrom(self, node):
        module = node.module
        for alias in node.names:
            imported_name = alias.name
            asname = alias.asname or imported_name
            
            # Track the full import path
            if module:
                full_name = f"{module}.{imported_name}"
                self.imports[asname] = full_name
                
                # Check if this is from our src directory
                if module.startswith("src.ontology_framework"):
                    # Try to find the actual implementation file
                    impl_path = self.src_path / module.replace("src.ontology_framework.", "").replace(".", "/")
                    if impl_path.exists():
                        logger.debug(f"Found implementation path: {impl_path}")
                        # Cache module classes
                        self._get_module_classes(module)
    
    def visit_FunctionDef(self, node):
        if node.name.startswith('test_'):
            self.current_test = node.name
            self.test_functions.append(node.name)
            self.dependencies[node.name] = set()
            
            # Check function arguments for dependencies
            for arg in node.args.args:
                if isinstance(arg.annotation, ast.Name):
                    class_name = arg.annotation.id
                    if class_name in self.imports:
                        impl_path = self.imports[class_name]
                        if impl_path.startswith("src.ontology_framework"):
                            self.dependencies[node.name].add((class_name, "parameter"))
                            
                            # Check if this is a class from our codebase
                            module_path = ".".join(impl_path.split(".")[:-1])
                            if class_name in self._get_module_classes(module_path):
                                self.dependencies[node.name].add((class_name, "class"))
                                # Add all methods of the class as potential dependencies
                                methods = self._get_class_methods(class_name, module_path)
                                for method in methods:
                                    self.dependencies[node.name].add((f"{class_name}.{method}", "method"))
            
            # Analyze function body for dependencies
            for stmt in node.body:
                self.visit(stmt)
            
            self.current_test = ""  # Reset to empty string
    
    def visit_Call(self, node):
        if not self.current_test:  # Check for empty string
            return
            
        # Analyze function calls for dependencies
        if isinstance(node.func, ast.Attribute):
            # Handle method calls
            if isinstance(node.func.value, ast.Name):
                obj_name = node.func.value.id
                method_name = node.func.attr
                
                if obj_name in self.imports:
                    impl_path = self.imports[obj_name]
                    if impl_path.startswith("src.ontology_framework"):
                        class_name = impl_path.split(".")[-1]
                        self.dependencies[self.current_test].add((class_name, "method"))
                        
                        # Add the method name as a dependency
                        self.dependencies[self.current_test].add((f"{class_name}.{method_name}", "method_call"))
                        
        elif isinstance(node.func, ast.Name):
            # Handle direct function calls
            if node.func.id in self.imports:
                impl_path = self.imports[node.func.id]
                if impl_path.startswith("src.ontology_framework"):
                    func_name = impl_path.split(".")[-1]
                    self.dependencies[self.current_test].add((func_name, "function"))
    
    def visit_Assert(self, node):
        if not self.current_test:  # Check for empty string
            return
            
        # Check assertions for dependencies
        if isinstance(node.test, ast.Call):
            self.visit(node.test)
            
    def visit_Assign(self, node):
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
                            self.dependencies[self.current_test].add((class_name, "variable"))
                            
                            # Check if this is a class from our codebase
                            module_path = ".".join(impl_path.split(".")[:-1])
                            if class_name in self._get_module_classes(module_path):
                                self.dependencies[self.current_test].add((class_name, "class"))
                                # Add all methods of the class as potential dependencies
                                methods = self._get_class_methods(class_name, module_path)
                                for method in methods:
                                    self.dependencies[self.current_test].add((f"{class_name}.{method}", "method"))

def analyze_test_file(test_file: Path) -> Dict[str, Set[Tuple[str, str]]]:
    """Analyze a test file for dependencies."""
    with open(test_file, 'r') as f:
        tree = ast.parse(f.read())
    
    analyzer = TestDependencyAnalyzer(test_file)
    analyzer.visit(tree)
    return analyzer.dependencies

def generate_test_dependencies(test_dir: Path) -> Graph:
    """Generate test dependencies graph from test files."""
    g = Graph()
    
    # Add namespace bindings
    g.bind("test", TEST)
    g.bind("impl", IMPL)
    g.bind("", BASE)
    
    # Process all test files
    for test_file in test_dir.glob("test_*.py"):
        logger.info(f"Analyzing {test_file}")
        dependencies = analyze_test_file(test_file)
        
        # Create test suite
        suite_name = test_file.stem.replace("test_", "")
        suite_uri = BASE[f"Test{suite_name.capitalize()}"]
        g.add((suite_uri, RDF.type, TEST.TestSuite))
        g.add((suite_uri, RDFS.label, Literal(f"{suite_name} Test Suite")))
        
        # Add test functions and their dependencies
        for test_name, deps in dependencies.items():
            test_uri = BASE[test_name]
            g.add((test_uri, RDF.type, TEST.Test))
            g.add((test_uri, RDFS.label, Literal(test_name)))
            g.add((suite_uri, TEST.hasTest, test_uri))
            
            for impl_class, dep_type in deps:
                dep_uri = IMPL[impl_class]
                g.add((test_uri, TEST.dependsOn, dep_uri))
                g.add((dep_uri, RDF.type, IMPL.Class))
                g.add((dep_uri, RDFS.label, Literal(impl_class)))
                g.add((dep_uri, TEST.dependencyType, Literal(dep_type)))
    
    return g

def main():
    """Main entry point."""
    try:
        test_dir = Path(__file__).parent
        g = generate_test_dependencies(test_dir)
        
        # Save the generated dependencies
        output_file = test_dir / "test_dependencies.ttl"
        g.serialize(output_file, format="turtle")
        logger.info(f"Generated test dependencies saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error generating test dependencies: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 