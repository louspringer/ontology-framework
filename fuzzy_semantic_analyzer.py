#!/usr/bin/env python3
# Fuzzy Semantic Analyzer
#
# This script builds a model from semantic comparison of individual Python code artifacts
# between the HEAD of the current branch and 'main', focusing on detecting syntax corruption
# from misplaced commas and analyzing functional loss caused by repository cleanup.
#
# Generated following ontology framework rules and ClaudeReflector constraints
# Ontology-Version: 1.0.0
# Behavioral-Profile: ClaudeReflector

import os
import sys
import ast
import re
import json
import subprocess
import logging
import tempfile
import time
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, NamedTuple, Union, Callable
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("fuzzy-semantic-analyzer")

# Define namespaces
CODE = Namespace("http://example.org/code#")
DIFF = Namespace("http://example.org/diff#")
FUNC = Namespace("http://example.org/function#")
CORRUPTION = Namespace("http://example.org/corruption#")
PARSER = Namespace("http://example.org/parser#")
TELEMETRY = Namespace("http://example.org/telemetry#")
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
PDCA = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/pdca#")

class ParserType(Enum):
    """Types of parsers available for semantic extraction."""
    AST = "ast"
    REGEX = "regex"
    TEXT = "text"

@dataclass
class ParserTelemetry:
    """Telemetry data for parser performance."""
    parser_type: ParserType
    start_time: float
    end_time: float = 0.0
    success_rate: float = 0.0
    elements_extracted: int = 0
    corruption_count: int = 0
    error_count: int = 0
    confidence_score: float = 0.0
    file_path: str = ""
    commit: str = ""
    errors: List[str] = field(default_factory=list)
    
    @property
    def parse_time_ms(self) -> float:
        """Calculate parse time in milliseconds."""
        return (self.end_time - self.start_time) * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert telemetry to dictionary for logging."""
        result = asdict(self)
        result['parse_time_ms'] = self.parse_time_ms
        result['parser_type'] = self.parser_type.value
        return result

@dataclass
class FunctionSignature:
    """Represents a function signature for semantic comparison."""
    name: str
    args: List[str] = field(default_factory=list)
    kwargs: List[Tuple[str, Optional[str]]] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    return_annotation: Optional[str] = None
    lineno: int = 0
    confidence: float = 1.0
    parser_source: ParserType = ParserType.AST

@dataclass
class ClassSignature:
    """Represents a class signature for semantic comparison."""
    name: str
    bases: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    methods: List[FunctionSignature] = field(default_factory=list)
    lineno: int = 0
    confidence: float = 1.0
    parser_source: ParserType = ParserType.AST

@dataclass
class ImportStatement:
    """Represents an import statement."""
    module: str
    names: List[str] = field(default_factory=list)
    is_from_import: bool = False
    lineno: int = 0
    confidence: float = 1.0
    parser_source: ParserType = ParserType.AST

@dataclass
class SyntaxError:
    """Represents a syntax error in the code."""
    message: str
    lineno: int
    confidence: float = 1.0
    parser_source: ParserType = ParserType.AST

@dataclass
class CommaCorruption:
    """Represents a comma corruption in the code."""
    message: str
    lineno: int
    confidence: float = 1.0
    parser_source: ParserType = ParserType.AST

@dataclass
class FileArtifact:
    """Represents a Python file artifact for semantic comparison."""
    path: str
    functions: List[FunctionSignature] = field(default_factory=list)
    classes: List[ClassSignature] = field(default_factory=list)
    imports: List[ImportStatement] = field(default_factory=list)
    syntax_errors: List[SyntaxError] = field(default_factory=list)
    comma_corruptions: List[CommaCorruption] = field(default_factory=list)
    telemetry: Dict[ParserType, ParserTelemetry] = field(default_factory=dict)

class ParserStrategy(ABC):
    """Abstract base class for parser strategies."""
    
    @abstractmethod
    def parse(self, content: str, file_path: str, commit: str) -> Tuple[FileArtifact, ParserTelemetry]:
        """Parse the content and return a file artifact and telemetry."""
        pass

class ASTParserStrategy(ParserStrategy):
    """Parser strategy using Python's built-in AST module."""
    
    def parse(self, content: str, file_path: str, commit: str) -> Tuple[FileArtifact, ParserTelemetry]:
        """Parse the content using AST."""
        telemetry = ParserTelemetry(
            parser_type=ParserType.AST,
            start_time=time.time(),
            file_path=file_path,
            commit=commit
        )
        
        functions = []
        classes = []
        imports = []
        syntax_errors = []
        
        try:
            tree = ast.parse(content)
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(ImportStatement(
                            module=name.name,
                            names=[name.name],
                            is_from_import=False,
                            lineno=node.lineno,
                            parser_source=ParserType.AST
                        ))
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    names = [n.name for n in node.names]
                    imports.append(ImportStatement(
                        module=module,
                        names=names,
                        is_from_import=True,
                        lineno=node.lineno,
                        parser_source=ParserType.AST
                    ))
            
            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # Skip methods (they'll be handled with classes)
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.iter_parents(tree, node)):
                        docstring = ast.get_docstring(node)
                        
                        # Get arguments
                        args = []
                        kwargs = []
                        
                        for arg in node.args.args:
                            args.append(arg.arg)
                        
                        for kwarg in node.args.kwonlyargs:
                            default = None
                            if kwarg.annotation:
                                try:
                                    default = ast.unparse(kwarg.annotation)
                                except:
                                    default = str(kwarg.annotation)
                            kwargs.append((kwarg.arg, default))
                        
                        # Get decorators
                        decorators = []
                        for decorator in node.decorator_list:
                            try:
                                decorators.append(ast.unparse(decorator))
                            except:
                                decorators.append(str(decorator))
                        
                        # Get return annotation
                        return_annotation = None
                        if node.returns:
                            try:
                                return_annotation = ast.unparse(node.returns)
                            except:
                                return_annotation = str(node.returns)
                        
                        function = FunctionSignature(
                            name=node.name,
                            args=args,
                            kwargs=kwargs,
                            decorators=decorators,
                            docstring=docstring,
                            return_annotation=return_annotation,
                            lineno=node.lineno,
                            parser_source=ParserType.AST
                        )
                        functions.append(function)
            
            # Extract classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    
                    # Get base classes
                    bases = []
                    for base in node.bases:
                        try:
                            bases.append(ast.unparse(base))
                        except:
                            bases.append(str(base))
                    
                    # Get decorators
                    decorators = []
                    for decorator in node.decorator_list:
                        try:
                            decorators.append(ast.unparse(decorator))
                        except:
                            decorators.append(str(decorator))
                    
                    # Get methods
                    methods = []
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef) or isinstance(child, ast.AsyncFunctionDef):
                            method_docstring = ast.get_docstring(child)
                            
                            # Get arguments
                            method_args = []
                            method_kwargs = []
                            
                            for arg in child.args.args:
                                if arg.arg != "self" and arg.arg != "cls":
                                    method_args.append(arg.arg)
                            
                            for kwarg in child.args.kwonlyargs:
                                default = None
                                if kwarg.annotation:
                                    try:
                                        default = ast.unparse(kwarg.annotation)
                                    except:
                                        default = str(kwarg.annotation)
                                method_kwargs.append((kwarg.arg, default))
                            
                            # Get decorators
                            method_decorators = []
                            for decorator in child.decorator_list:
                                try:
                                    method_decorators.append(ast.unparse(decorator))
                                except:
                                    method_decorators.append(str(decorator))
                            
                            # Get return annotation
                            method_return_annotation = None
                            if child.returns:
                                try:
                                    method_return_annotation = ast.unparse(child.returns)
                                except:
                                    method_return_annotation = str(child.returns)
                            
                            method = FunctionSignature(
                                name=child.name,
                                args=method_args,
                                kwargs=method_kwargs,
                                decorators=method_decorators,
                                docstring=method_docstring,
                                return_annotation=method_return_annotation,
                                lineno=child.lineno,
                                parser_source=ParserType.AST
                            )
                            methods.append(method)
                    
                    class_sig = ClassSignature(
                        name=node.name,
                        bases=bases,
                        decorators=decorators,
                        docstring=docstring,
                        methods=methods,
                        lineno=node.lineno,
                        parser_source=ParserType.AST
                    )
                    classes.append(class_sig)
            
            # Update telemetry
            telemetry.end_time = time.time()
            telemetry.elements_extracted = len(functions) + len(classes) + len(imports)
            telemetry.success_rate = 1.0
            telemetry.confidence_score = 1.0
            
        except SyntaxError as e:
            telemetry.end_time = time.time()
            telemetry.error_count += 1
            telemetry.success_rate = 0.0
            telemetry.confidence_score = 0.0
            telemetry.errors.append(f"SyntaxError: {str(e)}")
            
            syntax_errors.append(SyntaxError(
                message=str(e),
                lineno=e.lineno if hasattr(e, 'lineno') else 0,
                parser_source=ParserType.AST
            ))
        
        # Detect comma corruptions
        comma_corruptions = self._detect_comma_corruption(content)
        
        # Create file artifact
        artifact = FileArtifact(
            path=file_path,
            functions=functions,
            classes=classes,
            imports=imports,
            syntax_errors=syntax_errors,
            comma_corruptions=comma_corruptions,
            telemetry={ParserType.AST: telemetry}
        )
        
        return artifact, telemetry
    
    def _detect_comma_corruption(self, content: str) -> List[CommaCorruption]:
        """Detect comma corruption in Python code."""
        corruptions = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            # Check for misplaced commas
            if "," in line:
                # Check for commas in unusual places
                if line.strip().startswith(",") and not line.strip().startswith(",,"):
                    corruptions.append(CommaCorruption(
                        message=f"Line starts with comma: {line}",
                        lineno=i+1,
                        parser_source=ParserType.AST
                    ))
                
                # Check for commas after keywords
                for keyword in ["def", "class", "import", "from", "return", "if", "elif", "else", "for", "while"]:
                    if f"{keyword} ," in line or f"{keyword}," in line:
                        corruptions.append(CommaCorruption(
                            message=f"Comma after keyword '{keyword}': {line}",
                            lineno=i+1,
                            parser_source=ParserType.AST
                        ))
                
                # Check for commas in function calls with no arguments
                if "( ," in line or "(," in line:
                    corruptions.append(CommaCorruption(
                        message=f"Comma after opening parenthesis: {line}",
                        lineno=i+1,
                        parser_source=ParserType.AST
                    ))
                
                # Check for double commas
                if ",," in line:
                    corruptions.append(CommaCorruption(
                        message=f"Double comma: {line}",
                        lineno=i+1,
                        parser_source=ParserType.AST
                    ))
        
        return corruptions

class RegexParserStrategy(ParserStrategy):
    """Parser strategy using regular expressions for robust parsing."""
    
    def parse(self, content: str, file_path: str, commit: str) -> Tuple[FileArtifact, ParserTelemetry]:
        """Parse the content using regular expressions."""
        telemetry = ParserTelemetry(
            parser_type=ParserType.REGEX,
            start_time=time.time(),
            file_path=file_path,
            commit=commit
        )
        
        functions = []
        classes = []
        imports = []
        syntax_errors = []
        comma_corruptions = []
        
        try:
            # Extract imports
            import_patterns = [
                # Regular import: import module
                r'^\s*import\s+([a-zA-Z0-9_.,\s]+)',
                # From import: from module import name
                r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import\s+([a-zA-Z0-9_.,\s*]+)'
            ]
            
            for i, line in enumerate(content.split('\n')):
                for pattern in import_patterns:
                    match = re.match(pattern, line)
                    if match:
                        if len(match.groups()) == 1:  # Regular import
                            modules = [m.strip() for m in match.group(1).split(',')]
                            for module in modules:
                                imports.append(ImportStatement(
                                    module=module,
                                    names=[module],
                                    is_from_import=False,
                                    lineno=i+1,
                                    confidence=0.9,
                                    parser_source=ParserType.REGEX
                                ))
                        elif len(match.groups()) == 2:  # From import
                            module = match.group(1)
                            names = [n.strip() for n in match.group(2).split(',')]
                            imports.append(ImportStatement(
                                module=module,
                                names=names,
                                is_from_import=True,
                                lineno=i+1,
                                confidence=0.9,
                                parser_source=ParserType.REGEX
                            ))
            
            # Extract function definitions
            function_pattern = r'^\s*def\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)(?:\s*->\s*([a-zA-Z0-9_. \[\],]+))?:'
            for i, line in enumerate(content.split('\n')):
                match = re.match(function_pattern, line)
                if match:
                    func_name = match.group(1)
                    args_str = match.group(2)
                    return_type = match.group(3)
                    
                    # Parse arguments
                    args = []
                    kwargs = []
                    if args_str:
                        arg_list = [a.strip() for a in args_str.split(',')]
                        for arg in arg_list:
                            if '=' in arg:
                                name, default = arg.split('=', 1)
                                kwargs.append((name.strip(), default.strip()))
                            else:
                                args.append(arg)
                    
                    # Look for docstring
                    docstring = None
                    if i+1 < len(content.split('\n')):
                        next_line = content.split('\n')[i+1].strip()
                        if next_line.startswith('"""') or next_line.startswith("'''"):
                            docstring = next_line
                    
                    functions.append(FunctionSignature(
                        name=func_name,
                        args=args,
                        kwargs=kwargs,
                        return_annotation=return_type,
                        docstring=docstring,
                        lineno=i+1,
                        confidence=0.8,
                        parser_source=ParserType.REGEX
                    ))
            
            # Extract class definitions
            class_pattern = r'^\s*class\s+([a-zA-Z0-9_]+)(?:\s*\(([^)]*)\))?:'
            for i, line in enumerate(content.split('\n')):
                match = re.match(class_pattern, line)
                if match:
                    class_name = match.group(1)
                    bases_str = match.group(2)
                    
                    # Parse base classes
                    bases = []
                    if bases_str:
                        bases = [b.strip() for b in bases_str.split(',')]
                    
                    # Look for docstring
                    docstring = None
                    if i+1 < len(content.split('\n')):
                        next_line = content.split('\n')[i+1].strip()
                        if next_line.startswith('"""') or next_line.startswith("'''"):
                            docstring = next_line
                    
                    # Find methods (simplified approach)
                    methods = []
                    method_pattern = r'^\s{4}def\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)(?:\s*->\s*([a-zA-Z0-9_. \[\],]+))?:'
                    for j, method_line in enumerate(content.split('\n')[i+1:]):
                        method_match = re.match(method_pattern, method_line)
                        if method_match:
                            method_name = method_match.group(1)
                            method_args_str = method_match.group(2)
                            method_return_type = method_match.group(3)
                            
                            # Parse arguments
                            method_args = []
                            method_kwargs = []
                            if method_args_str:
                                method_arg_list = [a.strip() for a in method_args_str.split(',')]
                                for arg in method_arg_list:
                                    if arg in ['self', 'cls']:
                                        continue
                                    if '=' in arg:
                                        name, default = arg.split('=', 1)
                                        method_kwargs.append((name.strip(), default.strip()))
                                    else:
                                        method_args.append(arg)
                            
                            methods.append(FunctionSignature(
                                name=method_name,
                                args=method_args,
                                kwargs=method_kwargs,
                                return_annotation=method_return_type,
                                lineno=i+j+2,
                                confidence=0.7,
                                parser_source=ParserType.REGEX
                            ))
                    
                    classes.append(ClassSignature(
                        name=class_name,
                        bases=bases,
                        docstring=docstring,
                        methods=methods,
                        lineno=i+1,
                        confidence=0.8,
                        parser_source=ParserType.REGEX
                    ))
            
            # Detect comma corruptions
            comma_corruptions = self._detect_comma_corruption(content)
            
            # Update telemetry
            telemetry.end_time = time.time()
            telemetry.elements_extracted = len(functions) + len(classes) + len(imports)
            telemetry.corruption_count = len(comma_corruptions)
            telemetry.success_rate = 0.9  # Regex is less reliable than AST
            telemetry.confidence_score = 0.8
            
        except Exception as e:
            telemetry.end_time = time.time()
            telemetry.error_count += 1
            telemetry.success_rate = 0.5  # Partial success
            telemetry.confidence_score = 0.5
            telemetry.errors.append(f"Error: {str(e)}")
        
        # Create file artifact
        artifact = FileArtifact(
            path=file_path,
            functions=functions,
            classes=classes,
            imports=imports,
            syntax_errors=syntax_errors,
            comma_corruptions=comma_corruptions,
            telemetry={ParserType.REGEX: telemetry}
        )
        
        return artifact, telemetry
    
    def _detect_comma_corruption(self, content: str) -> List[CommaCorruption]:
        """Detect comma corruption in Python code using regex patterns."""
        corruptions = []
        
        # Patterns for comma corruptions
        patterns = [
            (r'^\s*,', "Line starts with comma"),
            (r'(def|class|import|from|return|if|elif|else|for|while)\s*,', "Comma after keyword"),
            (r'\(\s*,', "Comma after opening parenthesis"),
            (r',\s*,', "Double comma")
        ]
        
        for i, line in enumerate(content.split('\n')):
            for pattern, message in patterns:
                if re.search(pattern, line):
                    corruptions.append(CommaCorruption(
                        message=f"{message}: {line}",
                        lineno=i+1,
                        confidence=0.9,
                        parser_source=ParserType.REGEX
                    ))
        
        return corruptions

class TextParserStrategy(ParserStrategy):
    """Parser strategy using simple text analysis for heavily corrupted files."""
    
    def parse(self, content: str, file_path: str, commit: str) -> Tuple[FileArtifact, ParserTelemetry]:
        """Parse the content using text analysis."""
        telemetry = ParserTelemetry(
            parser_type=ParserType.TEXT,
            start_time=time.time(),
            file_path=file_path,
            commit=commit
        )
        
        functions = []
        classes = []
        imports = []
        syntax_errors = []
        comma_corruptions = []
        
        try:
            lines = content.split('\n')
            
            # Simple heuristic: look for indentation patterns and keywords
            current_class = None
            current_indent = 0
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                indent = len(line) - len(line.lstrip())
                
                # Track indentation changes
                if indent < current_indent:
                    current_class = None
                current_indent = indent
                
                # Look for imports
                if stripped.startswith('import ') or stripped.startswith('from '):
                    # Very simple import extraction
                    if stripped.startswith('import '):
                        module = stripped[7:].strip()
                        imports.append(ImportStatement(
                            module=module,
                            names=[module],
                            is_from_import=False,
                            lineno=i+1,
                            confidence=0.6,
                            parser_source=ParserType.TEXT
                        ))
                    else:  # from import
                        parts = stripped.split(' import ')
                        if len(parts) == 2:
                            module = parts[0][5:].strip()  # Remove 'from '
                            names = [n.strip() for n in parts[1].split(',')]
                            imports.append(ImportStatement(
                                module=module,
                                names=names,
                                is_from_import=True,
                                lineno=i+1,
                                confidence=0.6,
                                parser_source=ParserType.TEXT
                            ))
                
                # Look for class definitions
                elif stripped.startswith('class '):
                    class_def = stripped[6:].split('(')[0].strip(':')
                    class_name = class_def.strip()
                    
                    # Extract base classes if present
                    bases = []
                    if '(' in stripped:
                        bases_str = stripped.split('(')[1].split(')')[0]
                        bases = [b.strip() for b in bases_str.split(',')]
                    
                    current_class = ClassSignature(
                        name=class_name,
                        bases=bases,
                        lineno=i+1,
                        confidence=0.6,
                        parser_source=ParserType.TEXT
                    )
                    classes.append(current_class)
                
                # Look for function/method definitions
                elif stripped.startswith('def '):
                    func_def = stripped[4:].split('(')[0].strip()
                    func_name = func_def.strip()
                    
                    # Extract arguments if present
                    args = []
                    if '(' in stripped and ')' in stripped:
                        args_str = stripped.split('(')[1].split(')')[0]
                        args = [a.strip() for a in args_str.split(',')]
                    
                    function = FunctionSignature(
                        name=func_name,
                        args=args,
                        lineno=i+1,
                        confidence=0.5,
                        parser_source=ParserType.TEXT
                    )
                    
                    # Add as method if inside a class
                    if current_class is not None:
                        current_class.methods.append(function)
                    else:
                        functions.append(function)
                
                # Look for syntax errors and comma corruptions
                if ',' in stripped:
                    # Check for common comma corruption patterns
                    if stripped.startswith(','):
                        comma_corruptions.append(CommaCorruption(
                            message=f"Line starts with comma: {stripped}",
                            lineno=i+1,
                            confidence=0.7,
                            parser_source=ParserType.TEXT
                        ))
                    
                    # Check for commas after keywords
                    for keyword in ["def", "class", "import", "from", "return", "if", "elif", "else", "for", "while"]:
                        if stripped.startswith(f"{keyword} ,") or stripped.startswith(f"{keyword},"):
                            comma_corruptions.append(CommaCorruption(
                                message=f"Comma after keyword '{keyword}': {stripped}",
                                lineno=i+1,
                                confidence=0.7,
                                parser_source=ParserType.TEXT
                            ))
            
            # Update telemetry
            telemetry.end_time = time.time()
            telemetry.elements_extracted = len(functions) + len(classes) + len(imports)
            telemetry.corruption_count = len(comma_corruptions)
            telemetry.success_rate = 0.7  # Text parsing is less reliable
            telemetry.confidence_score = 0.6
            
        except Exception as e:
            telemetry.end_time = time.time()
            telemetry.error_count += 1
            telemetry.success_rate = 0.3
            telemetry.confidence_score = 0.3
            telemetry.errors.append(f"Error: {str(e)}")
        
        # Create file artifact
        artifact = FileArtifact(
            path=file_path,
            functions=functions,
            classes=classes,
            imports=imports,
            syntax_errors=syntax_errors,
            comma_corruptions=comma_corruptions,
            telemetry={ParserType.TEXT: telemetry}
        )
        
        return artifact, telemetry

def analyze_semantic_differences(original_triples: List[Tuple[str, str, str]], 
                                modified_triples: List[Tuple[str, str, str]]) -> Dict[str, Any]:
    """
    Analyze semantic differences between two sets of triples.
    
    Args:
        original_triples: List of original triples, each as (subject, predicate, object)
        modified_triples: List of modified triples, each as (subject, predicate, object)
        
    Returns:
        Dictionary containing analysis results:
            - unchanged: List of triples that are unchanged
            - modified: List of dictionaries with original and modified triples and what changed
            - added: List of triples that were added
            - removed: List of triples that were removed
            - similarity_score: Score indicating similarity between the two sets
    """
    # Initialize result structure
    result = {
        "unchanged": [],
        "modified": [],
        "added": [],
        "removed": [],
        "similarity_score": 0.0
    }
    
    # Create dictionaries for faster lookup
    original_dict = {}
    for triple in original_triples:
        subject, predicate, obj = triple
        if subject not in original_dict:
            original_dict[subject] = []
        original_dict[subject].append((predicate, obj))
    
    modified_dict = {}
    for triple in modified_triples:
        subject, predicate, obj = triple
        if subject not in modified_dict:
            modified_dict[subject] = []
        modified_dict[subject].append((predicate, obj))
    
    # Find unchanged, modified, and removed triples
    for triple in original_triples:
        subject, predicate, obj = triple
        
        # Check if the subject exists in modified triples
        if subject in modified_dict:
            # Check if the exact triple exists in modified triples
            if (predicate, obj) in modified_dict[subject]:
                result["unchanged"].append(triple)
            else:
                # The subject exists but with different predicate or object
                # Find the closest match for this subject
                for mod_pred, mod_obj in modified_dict[subject]:
                    changes = []
                    if predicate != mod_pred:
                        changes.append("predicate")
                    if obj != mod_obj:
                        changes.append("object")
                    
                    if changes:  # If there are changes
                        result["modified"].append({
                            "original": triple,
                            "modified": (subject, mod_pred, mod_obj),
                            "changes": changes
                        })
                        break
        else:
            # Subject doesn't exist in modified triples
            result["removed"].append(triple)
    
    # Find added triples
    for triple in modified_triples:
        subject, predicate, obj = triple
        
        # Check if this is a new subject
        if subject not in original_dict:
            result["added"].append(triple)
        else:
            # Check if this is a new predicate-object pair for an existing subject
            if (predicate, obj) not in original_dict[subject]:
                # Check if it's not already in the modified list
                is_modification = False
                for mod_item in result["modified"]:
                    if mod_item["modified"] == triple:
                        is_modification = True
                        break
                
                if not is_modification:
                    result["added"].append(triple)
    
    # Calculate similarity score using the formula:
    # (unchanged_count + 0.5 * modified_count) / original_count
    unchanged_count = len(result["unchanged"])
    modified_count = len(result["modified"])
    original_count = len(original_triples)
    
    if original_count > 0:
        result["similarity_score"] = (unchanged_count + 0.5 * modified_count) / original_count
    else:
        result["similarity_score"] = 0.0
    
    return result

class FuzzySemanticAnalyzer:
    """Analyzes semantic differences between Git commits using multiple parser strategies."""
    
    def __init__(self, parsers: Optional[List[ParserStrategy]] = None):
        """Initialize the fuzzy semantic analyzer."""
        self.graph = Graph()
        self.setup_graph()
        self.current_branch = self.get_current_branch()
        
        # Initialize parser strategies
        self.parsers = parsers or [
            ASTParserStrategy(),
            RegexParserStrategy(),
            TextParserStrategy()
        ]
        
        logger.info(f"Initialized FuzzySemanticAnalyzer with {len(self.parsers)} parser strategies")
        logger.info(f"Current branch: {self.current_branch}")
    
    def setup_graph(self):
        """Set up the RDF graph with namespaces."""
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph
