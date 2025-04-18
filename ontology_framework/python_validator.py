#!/usr/bin/env python3
"""Python code validator using SHACL shapes."""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Union
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
import tokenize
import io

# Define namespaces
PYVAL = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/python_validation#")

class PythonValidator:
    """Validates Python code structure using SHACL shapes."""
    
    def __init__(self):
        """Initialize validator with SHACL shapes."""
        self.shapes_graph = Graph()
        shapes_file = Path("guidance/modules/python_validation.ttl")
        self.shapes_graph.parse(shapes_file, format="turtle")
        
    def validate_file(self, file_path: Union[str, Path]) -> List[str]:
        """Validate a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of validation errors
        """
        errors = []
        try:
            # Create RDF graph for the Python code
            code_graph = Graph()
            code_graph.bind("pyval", PYVAL)
            
            # Parse Python file
            with open(file_path, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
            # Add code structure to graph
            file_node = URIRef(f"file://{file_path}")
            code_graph.add((file_node, RDF.type, PYVAL.PythonCode))
            
            # Validate indentation
            with open(file_path, 'rb') as f:
                indentation = self._get_indentation(f)
                if indentation != 4:  # Standard Python indentation is 4 spaces
                    errors.append(f"Invalid indentation: found {indentation} spaces, expected 4 spaces")
                code_graph.add((file_node, PYVAL.indentation, Literal(indentation)))
            
            # Validate line length
            max_line_length = max(len(line.rstrip()) for line in content.split('\n'))
            if max_line_length > 88:  # Black's default line length
                errors.append(f"Line too long: {max_line_length} characters")
            code_graph.add((file_node, PYVAL.lineLength, Literal(max_line_length)))
            
            # Validate docstrings and structure
            has_docstring = ast.get_docstring(tree) is not None
            if not has_docstring:
                errors.append("Missing module docstring")
            code_graph.add((file_node, PYVAL.hasDocstring, Literal(has_docstring)))
            
            # Validate classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_node = URIRef(f"file://{file_path}#class_{node.name}")
                    code_graph.add((class_node, RDF.type, PYVAL.PythonClass))
                    
                    # Check for __init__
                    has_init = any(
                        isinstance(n, ast.FunctionDef) and n.name == "__init__"
                        for n in node.body
                    )
                    code_graph.add((class_node, PYVAL.hasInit, Literal(has_init)))
                    
                    # Check class docstring
                    class_doc = ast.get_docstring(node)
                    if not class_doc:
                        errors.append(f"Missing docstring for class {node.name}")
                    code_graph.add((
                        class_node,
                        PYVAL.classDocstring,
                        Literal(class_doc if class_doc else "")
                    ))
                    
                # Validate methods
                elif isinstance(node, ast.FunctionDef):
                    method_node = URIRef(f"file://{file_path}#method_{node.name}")
                    code_graph.add((method_node, RDF.type, PYVAL.PythonMethod))
                    
                    # Check type hints
                    has_type_hints = (
                        node.returns is not None and
                        all(arg.annotation is not None for arg in node.args.args)
                    )
                    if not has_type_hints:
                        errors.append(f"Missing type hints in method {node.name}")
                    code_graph.add((method_node, PYVAL.hasTypeHints, Literal(has_type_hints)))
                    
                    # Check return type
                    has_return_type = node.returns is not None
                    if not has_return_type:
                        errors.append(f"Missing return type hint in method {node.name}")
                    code_graph.add((method_node, PYVAL.hasReturnType, Literal(has_return_type)))
                    
                    # Check method docstring
                    method_doc = ast.get_docstring(node)
                    if not method_doc:
                        errors.append(f"Missing docstring for method {node.name}")
                    code_graph.add((
                        method_node,
                        PYVAL.methodDocstring,
                        Literal(method_doc if method_doc else "")
                    ))
            
            # Validate against SHACL shapes
            from pyshacl import validate
            conforms, results_graph, results_text = validate(
                code_graph,
                shacl_graph=self.shapes_graph,
                ont_graph=None,
                inference='none',
                abort_on_error=False
            )
            
            if not conforms:
                errors.extend(results_text.split('\n'))
                
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            
        return errors
        
    def _get_indentation(self, file: io.BufferedReader) -> int:
        """Get the indentation level of a Python file.
        
        Args:
            file: File object to analyze
            
        Returns:
            Number of spaces used for indentation
        """
        try:
            tokens = tokenize.tokenize(file.readline)
            for token in tokens:
                if token.type == tokenize.INDENT:
                    return len(token.string)
        except tokenize.TokenError:
            pass
        return 0  # Default to 0 if no indentation found 