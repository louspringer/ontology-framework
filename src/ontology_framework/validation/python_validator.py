import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.term import Node
import pyshacl

PY = Namespace("http://example.org/python#")

class PythonValidator:
    """Validates Python code using SHACL shapes."""
    
    def __init__(self, shapes_file: str = "tests/test_data/python_shapes.ttl"):
        """Initialize the validator with SHACL shapes.
        
        Args:
            shapes_file: Path to the SHACL shapes file
        """
        self.shapes_graph = Graph()
        self.shapes_graph.parse(shapes_file, format="turtle")
        self.data_graph = Graph()
        self.data_graph.bind("py", PY)
        
    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation from a function definition.
        
        Args:
            node: The AST function definition node
            
        Returns:
            Optional[str]: The return type as a string or None if not present
        """
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
            elif isinstance(node.returns, ast.Subscript):
                # Handle generic types like List[str], Optional[int], etc.
                if isinstance(node.returns.value, ast.Name):
                    return node.returns.value.id
        return None
        
    def _create_class_node(self, graph: Graph, class_def: ast.ClassDef) -> URIRef:
        """Create an RDF node for a class definition.
        
        Args:
            graph: The RDF graph to add the class to
            class_def: The AST class definition node
            
        Returns:
            URIRef: The URI reference for the created class node
        """
        class_uri = URIRef(f"{PY}{class_def.name}")
        graph.add((class_uri, RDF.type, PY.Class))
        graph.add((class_uri, PY.name, Literal(class_def.name)))
        
        # Add docstring if present
        docstring = ast.get_docstring(class_def)
        if docstring:
            graph.add((class_uri, PY.docstring, Literal(docstring)))
            
        return class_uri
        
    def _create_method_node(self, node: ast.FunctionDef) -> BNode:
        """Create a method node with its properties."""
        method_node = BNode()
        self.data_graph.add((method_node, RDF.type, PY.Method))
        self.data_graph.add((method_node, PY.name, Literal(node.name)))
        self.data_graph.add((method_node, PY.docstring, Literal(ast.get_docstring(node) or "")))

        # Handle return type
        return_type = self._get_return_type(node)
        if node.name == '__init__':
            # Special case for __init__ methods
            no_return = BNode()
            self.data_graph.add((no_return, RDF.type, PY.NoReturnType))
            self.data_graph.add((no_return, PY.name, Literal('__init__')))
            self.data_graph.add((method_node, PY.returnType, no_return))
        else:
            self.data_graph.add((method_node, PY.returnType, Literal(return_type or 'Any')))

        for arg in node.args.args:
            if arg.arg != 'self':  # Skip self parameter
                param_node = self._create_parameter_node(arg)
                self.data_graph.add((method_node, PY.hasParameter, param_node))

        return method_node

    def _create_parameter_node(self, node: ast.arg) -> BNode:
        """Create a parameter node with its properties."""
        param_node = BNode()
        self.data_graph.add((param_node, RDF.type, PY.Parameter))
        self.data_graph.add((param_node, PY.name, Literal(node.arg)))
        self.data_graph.add((param_node, PY.type, Literal(self._get_type_annotation(node.annotation) or 'Any')))
        return param_node

    def _get_type_annotation(self, annotation: Optional[ast.AST]) -> Optional[str]:
        """Convert a type annotation AST node to a string."""
        if annotation is None:
            return None
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            return f"{annotation.value.id}[{self._get_type_annotation(annotation.slice)}]"
        return 'Any'

    def validate_node(self, node: ast.AST) -> Dict[str, Any]:
        """Validate a Python AST node against SHACL shapes."""
        self.data_graph = Graph()  # Reset graph for new validation
        self.data_graph.bind('py', PY)

        # Process all nodes in the AST
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef):
                self._process_class(child)
            elif isinstance(child, ast.FunctionDef) and not any(
                isinstance(parent, ast.ClassDef) for parent in ast.walk(node)
            ):
                # Only process standalone functions (not methods)
                self._process_function(child)

        # Debug output
        print("\nProcessed Data Graph:")
        print(self.data_graph.serialize(format='turtle'))

        conforms, results_graph, results = pyshacl.validate(
            self.data_graph,
            shacl_graph=self.shapes_graph,
            inference='none',
            abort_on_first=False,
            allow_warnings=True
        )

        return {
            'conforms': conforms,
            'results': self._process_validation_results(results_graph) if not conforms else []
        }

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate a Python file against SHACL shapes."""
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        return self.validate_node(tree)

    def _process_class(self, node: ast.ClassDef) -> None:
        """Process a class definition and add it to the data graph."""
        class_node = BNode()
        self.data_graph.add((class_node, RDF.type, PY.Class))
        self.data_graph.add((class_node, PY.name, Literal(node.name)))
        self.data_graph.add((class_node, PY.docstring, Literal(ast.get_docstring(node) or "")))

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_node = self._create_method_node(item)
                self.data_graph.add((class_node, PY.hasMethod, method_node))

    def _process_function(self, node: ast.FunctionDef) -> None:
        """Process a function definition and add it to the data graph."""
        method_node = self._create_method_node(node)
        self.data_graph.add((method_node, PY.name, Literal(node.name)))

    def _process_validation_results(self, results_graph: Graph) -> List[Dict[str, str]]:
        """Process SHACL validation results into a list of violations."""
        violations = []
        for result in results_graph.subjects(RDF.type, URIRef("http://www.w3.org/ns/shacl#ValidationResult")):
            message = str(list(results_graph.objects(result, URIRef("http://www.w3.org/ns/shacl#resultMessage")))[0])
            violations.append({
                'message': message,
                'severity': 'error'
            })
        return violations 