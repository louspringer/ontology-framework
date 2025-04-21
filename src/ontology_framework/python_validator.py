"""Python code validation functionality for the ontology framework.

This module provides functionality for validating Python code against ontology
requirements, including type checking, naming conventions, and documentation.
"""

from typing import Dict, List, Optional, Set, Union
import ast
import logging
from pathlib import Path
import re
from .exceptions import ValidationError

logger = logging.getLogger(__name__)

class PythonValidator:
    """Validates Python code against ontology requirements."""
    
    def __init__(self, source_file: Union[str, Path]):
        """Initialize Python validator.
        
        Args:
            source_file: Path to Python source file
            
        Raises:
            ValidationError: If source file cannot be loaded
        """
        self.source_file = Path(source_file)
        try:
            with open(self.source_file, "r") as f:
                self.source = f.read()
            self.tree = ast.parse(self.source)
            logger.info(f"Loaded Python source from {self.source_file}")
        except Exception as e:
            raise ValidationError(f"Failed to load Python source: {str(e)}")
            
    def validate_types(self) -> List[str]:
        """Validate type hints and annotations.
        
        Returns:
            List of type validation issues
        """
        issues = []
        
        class TypeChecker(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                
            def visit_FunctionDef(self, node):
                # Check return type annotation
                if not node.returns:
                    self.issues.append(f"Missing return type for function {node.name}")
                    
                # Check argument type annotations
                for arg in node.args.args:
                    if not arg.annotation:
                        self.issues.append(f"Missing type annotation for argument {arg.arg} in function {node.name}")
                        
                self.generic_visit(node)
                
            def visit_AnnAssign(self, node):
                if not node.annotation:
                    if isinstance(node.target, ast.Name):
                        self.issues.append(f"Missing type annotation for variable {node.target.id}")
                self.generic_visit(node)
                
        checker = TypeChecker()
        checker.visit(self.tree)
        issues.extend(checker.issues)
        
        return issues
        
    def validate_docstrings(self) -> List[str]:
        """Validate docstring presence and format.
        
        Returns:
            List of docstring validation issues
        """
        issues = []
        
        class DocstringChecker(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                
            def visit_Module(self, node):
                if not ast.get_docstring(node):
                    self.issues.append("Missing module docstring")
                self.generic_visit(node)
                
            def visit_ClassDef(self, node):
                if not ast.get_docstring(node):
                    self.issues.append(f"Missing docstring for class {node.name}")
                self.generic_visit(node)
                
            def visit_FunctionDef(self, node):
                docstring = ast.get_docstring(node)
                if not docstring:
                    self.issues.append(f"Missing docstring for function {node.name}")
                elif "Args:" not in docstring or "Returns:" not in docstring:
                    self.issues.append(f"Incomplete docstring for function {node.name}")
                self.generic_visit(node)
                
        checker = DocstringChecker()
        checker.visit(self.tree)
        issues.extend(checker.issues)
        
        return issues
        
    def validate_naming(self) -> List[str]:
        """Validate naming conventions.
        
        Returns:
            List of naming convention issues
        """
        issues = []
        
        class NamingChecker(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                
            def visit_ClassDef(self, node):
                if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
                    self.issues.append(f"Invalid class name (should be CamelCase): {node.name}")
                self.generic_visit(node)
                
            def visit_FunctionDef(self, node):
                if not re.match(r"^[a-z][a-z0-9_]*$", node.name):
                    self.issues.append(f"Invalid function name (should be snake_case): {node.name}")
                self.generic_visit(node)
                
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    if not re.match(r"^[a-z][a-z0-9_]*$", node.id):
                        self.issues.append(f"Invalid variable name (should be snake_case): {node.id}")
                self.generic_visit(node)
                
        checker = NamingChecker()
        checker.visit(self.tree)
        issues.extend(checker.issues)
        
        return issues
        
    def validate_imports(self) -> List[str]:
        """Validate import statements.
        
        Returns:
            List of import validation issues
        """
        issues = []
        
        class ImportChecker(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                self.imports = set()
                
            def visit_Import(self, node):
                for name in node.names:
                    if name.name in self.imports:
                        self.issues.append(f"Duplicate import: {name.name}")
                    self.imports.add(name.name)
                    
            def visit_ImportFrom(self, node):
                for name in node.names:
                    full_name = f"{node.module}.{name.name}"
                    if full_name in self.imports:
                        self.issues.append(f"Duplicate import: {full_name}")
                    self.imports.add(full_name)
                    
        checker = ImportChecker()
        checker.visit(self.tree)
        issues.extend(checker.issues)
        
        return issues 