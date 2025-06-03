#!/usr/bin/env python3
""""Semantic Diff Analyzer

is script builds a model from semantic comparison of individual Python code artifacts
tween the HEAD of the current branch and 'main', focusing on detecting syntax corruption
om misplaced commas and analyzing functional loss caused by repository cleanup.

nerated following ontology framework rules and ClaudeReflector constraints
tology-Version: 1.0.0
havioral-Profile: ClaudeReflector
""""""


import os
import sys
import ast
import subprocess
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, NamedTuple, Union
from dataclasses import dataclass
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("semantic-diff-analyzer")

# Define namespaces
CODE = Namespace("http://example.org/code#")
DIFF = Namespace("http://example.org/diff#")
FUNC = Namespace("http://example.org/function#")
CORRUPTION = Namespace("http://example.org/corruption#")
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
PDCA = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/pdca#")

@dataclass
class FunctionSignature:
    """Represents a function signature for semantic comparison."""
    name: str
    args: List[str]
    kwargs: List[Tuple[str, Optional[str]]]
    decorators: List[str]
    docstring: Optional[str]
    return_annotation: Optional[str]
    lineno: int
    
    def to_rdf(self, graph: Graph, file_uri: URIRef) -> URIRef:
        """Convert function signature to RDF."""
        func_uri = URIRef(f"{file_uri}#{self.name}")
        graph.add((func_uri, RDF.type, FUNC.Function))
        graph.add((func_uri, RDFS.label, Literal(self.name)))
        graph.add((func_uri, FUNC.definedIn, file_uri))
        graph.add((func_uri, FUNC.lineNumber, Literal(self.lineno, datatype=XSD.integer)))
        
        if self.docstring:
            graph.add((func_uri, FUNC.hasDocstring, Literal(self.docstring)))
        
        if self.return_annotation:
            graph.add((func_uri, FUNC.hasReturnType, Literal(self.return_annotation)))
        
        for arg in self.args:
            arg_node = BNode()
            graph.add((arg_node, RDF.type, FUNC.Argument))
            graph.add((arg_node, RDFS.label, Literal(arg)))
            graph.add((func_uri, FUNC.hasArgument, arg_node))
        
        for kwarg, default in self.kwargs:
            kwarg_node = BNode()
            graph.add((kwarg_node, RDF.type, FUNC.KeywordArgument))
            graph.add((kwarg_node, RDFS.label, Literal(kwarg)))
            if default:
                graph.add((kwarg_node, FUNC.hasDefault, Literal(default)))
            graph.add((func_uri, FUNC.hasKeywordArgument, kwarg_node))
        decorators:
            dec_node = BNode()
            graph.add((dec_node, RDF.type, FUNC.Decorator))
            graph.add((dec_node, RDFS.label, Literal(decorator)))
            graph.add((func_uri, FUNC.hasDecorator, dec_node))
        
        return func_uri

@dataclass
class ClassSignature:
    """Represents a class signature for semantic comparison."""
    name: str
    bases: List[str]
    decorators: List[str]
    docstring: Optional[str]
    methods: List[FunctionSignature]
    lineno: int
    
    def to_rdf(self, graph: Graph, file_uri: URIRef) -> URIRef:
        """Convert class signature to RDF."""
        class_uri = URIRef(f"{file_uri}#{self.name}")
        graph.add((class_uri, RDF.type, FUNC.Class))
        graph.add((class_uri, RDFS.label, Literal(self.name)))
        graph.add((class_uri, FUNC.definedIn, file_uri))
        graph.add((class_uri, FUNC.lineNumber, Literal(self.lineno, datatype=XSD.integer)))
        
        if self.docstring:
            graph.add((class_uri, FUNC.hasDocstring, Literal(self.docstring)))
        
        for base in self.bases:
            graph.add((class_uri, FUNC.inheritsFrom, Literal(base)))
        
        for decorator in self.decorators:
            dec_node = BNode()
            graph.add((dec_node, RDF.type, FUNC.Decorator))
            graph.add((dec_node, RDFS.label, Literal(decorator)))
            graph.add((class_uri, FUNC.hasDecorator, dec_node))
        
        for method in self.methods:
            method_uri = method.to_rdf(graph, class_uri)
            graph.add((class_uri, FUNC.hasMethod, method_uri))
        
        return class_uri

@dataclass
class FileArtifact:
    """Represents a Python file artifact for semantic comparison."""
    path: str
    functions: List[FunctionSignature]
    classes: List[ClassSignature]
    imports: List[str]
    syntax_errors: List[str]
    comma_corruptions: List[Tuple[int, str]]
    
    def to_rdf(self, graph: Graph) -> URIRef:
        """Convert file artifact to RDF."""
        file_uri = URIRef(f"http://example.org/file/{self.path}")
        graph.add((file_uri, RDF.type, CODE.PythonFile))
        graph.add((file_uri, RDFS.label, Literal(self.path)))
        graph.add((file_uri, CODE.path, Literal(self.path)))
        
        for function in self.functions:
            func_uri = function.to_rdf(graph, file_uri)
            graph.add((file_uri, CODE.hasFunction, func_uri))
        
        for class_sig in self.classes:
            class_uri = class_sig.to_rdf(graph, file_uri)
            graph.add((file_uri, CODE.hasClass, class_uri))
        
        for imp in self.imports:
            imp_node = BNode()
            graph.add((imp_node, RDF.type, CODE.Import))
            graph.add((imp_node, RDFS.label, Literal(imp)))
            graph.add((file_uri, CODE.hasImport, imp_node))
        
        for lineno, error in self.syntax_errors:
            error_node = BNode()
            graph.add((error_node, RDF.type, CODE.SyntaxError))
            graph.add((error_node, CODE.lineNumber, Literal(lineno, datatype=XSD.integer)))
            graph.add((error_node, RDFS.label, Literal(error)))
            graph.add((file_uri, CODE.hasSyntaxError, error_node))
        
        for lineno, corruption in self.comma_corruptions:
            corruption_node = BNode()
            graph.add((corruption_node, RDF.type, CORRUPTION.CommaCorruption))
            graph.add((corruption_node, CODE.lineNumber, Literal(lineno, datatype=XSD.integer)))
            graph.add((corruption_node, RDFS.label, Literal(corruption)))
            graph.add((file_uri, CORRUPTION.hasCommaCorruption, corruption_node))
        
        return file_uri

class SemanticDiffAnalyzer:
    """Analyzes semantic differences between Git commits."""
    
    def __init__(self):
        """Initialize the semantic diff analyzer."""
        self.graph = Graph()
        self.setup_graph()
        self.current_branch = self.get_current_branch()
        logger.info(f"Current branch: {self.current_branch}")
    
    def setup_graph(self):
        """Set up the RDF graph with namespaces."""
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        self.graph.bind("code", CODE)
        self.graph.bind("diff", DIFF)
        self.graph.bind("func", FUNC)
        self.graph.bind("corruption", CORRUPTION)
        self.graph.bind("guidance", GUIDANCE)
        self.graph.bind("pdca", PDCA)
    
    def get_current_branch(self) -> str:
        """Get the name of the current Git branch."""
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    
    def get_python_files(self) -> List[str]:
        """Get a list of all Python files in the repository."""
        result = subprocess.run(
            ["git", "ls-files", "*.py"],
            capture_output=True,
            text=True,
            check=True
        )
        return [file for file in result.stdout.strip().split("\n") if file]
    
    def get_file_content(self, file_path: str, commit: str = "HEAD") -> str:
        """Get the content of a file at a specific commit."""
        try:
            result = subprocess.run(
                ["git", "show", f"{commit}:{file_path}"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                logger.warning(f"File {file_path} not found in commit {commit}")
                return ""
            return result.stdout
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return ""
    
    def detect_comma_corruption(self, content: str) -> List[Tuple[int, str]]:
        """Detect comma corruption in Python code."""
        corruptions = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            # Check for misplaced commas
            if "," in line:
                # Check for commas in unusual places
                if line.strip().startswith(",") and not line.strip().startswith(",,"):
                    corruptions.append((i+1, f"Line starts with comma: {line}"))
                
                # Check for commas after keywords
                for keyword in ["def", "class", "import", "from", "return", "if", "elif", "else", "for", "while"]:
                    if f"{keyword} ," in line or f"{keyword}," in line:
                        corruptions.append((i+1, f"Comma after keyword '{keyword}': {line}"))
                
                # Check for commas in function calls with no arguments
                if "( ," in line or "(," in line:
                    corruptions.append((i+1, f"Comma after opening parenthesis: {line}"))
                
                # Check for double commas
                if ",," in line:
                    corruptions.append((i+1, f"Double comma: {line}"))
        
        return corruptions
    
    def parse_python_file(self, content: str) -> FileArtifact:
        """Parse a Python file and extract semantic information."""
        functions = []
        classes = []
        imports = []
        syntax_errors = []
        
        # Try to parse the file
        try:
            tree = ast.parse(content)
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        imports.append(f"{module}.{name.name}")
            
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
                                default = ast.unparse(kwarg.annotation)
                            kwargs.append((kwarg.arg, default))
                        
                        # Get decorators
                        decorators = []
                        for decorator in node.decorator_list:
                            decorators.append(ast.unparse(decorator))
                        
                        # Get return annotation
                        return_annotation = None
                        if node.returns:
                            return_annotation = ast.unparse(node.returns)
                        
                        function = FunctionSignature(
                            name=node.name,
                            args=args,
                            kwargs=kwargs,
                            decorators=decorators,
                            docstring=docstring,
                            return_annotation=return_annotation,
                            lineno=node.lineno
                        )
                        functions.append(function)
            
            # Extract classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    
                    # Get base classes
                    bases = []
                    for base in node.bases:
                        bases.append(ast.unparse(base))
                    
                    # Get decorators
                    decorators = []
                    for decorator in node.decorator_list:
                        decorators.append(ast.unparse(decorator))
                    
                    # Get methods
                    methods = []
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef) or isinstance(child, ast.AsyncFunctionDef):
                            method_docstring = ast.get_docstring(child)
                            
                            # Get arguments
                            args = []
                            kwargs = []
                            
                            for arg in child.args.args:
                                if arg.arg != "self" and arg.arg != "cls":
                                    args.append(arg.arg)
                            
                            for kwarg in child.args.kwonlyargs:
                                default = None
                                if kwarg.annotation:
                                    default = ast.unparse(kwarg.annotation)
                                kwargs.append((kwarg.arg, default))
                            
                            # Get decorators
                            method_decorators = []
                            for decorator in child.decorator_list:
                                method_decorators.append(ast.unparse(decorator))
                            
                            # Get return annotation
                            return_annotation = None
                            if child.returns:
                                return_annotation = ast.unparse(child.returns)
                            
                            method = FunctionSignature(
                                name=child.name,
                                args=args,
                                kwargs=kwargs,
                                decorators=method_decorators,
                                docstring=method_docstring,
                                return_annotation=return_annotation,
                                lineno=child.lineno
                            )
                            methods.append(method)
                    
                    class_sig = ClassSignature(
                        name=node.name,
                        bases=bases,
                        decorators=decorators,
                        docstring=docstring,
                        methods=methods,
                        lineno=node.lineno
                    )
                    classes.append(class_sig)
                    
        except SyntaxError as e:
            syntax_errors.append((e.lineno, str(e)))
        
        # Detect comma corruptions
        comma_corruptions = self.detect_comma_corruption(content)
        
        return FileArtifact(
            path="",  # Will be set by the caller
            functions=functions,
            classes=classes,
            imports=imports,
            syntax_errors=syntax_errors,
            comma_corruptions=comma_corruptions
        )
    
    def analyze_file(self, file_path: str, commit: str = "HEAD") -> Optional[FileArtifact]:
        """Analyze a Python file at a specific commit."""
        content = self.get_file_content(file_path, commit)
        if not content:
            return None
        
        artifact = self.parse_python_file(content)
        artifact.path = file_path
        return artifact
    
    def compare_artifacts(self, current: FileArtifact, previous: FileArtifact) -> Dict[str, Any]:
        """Compare two file artifacts and identify differences."""
        diff = {
            "path": current.path,
            "added_functions": [],
            "removed_functions": [],
            "modified_functions": [],
            "added_classes": [],
            "removed_classes": [],
            "modified_classes": [],
            "syntax_errors_fixed": [],
            "syntax_errors_introduced": [],
            "comma_corruptions_fixed": [],
            "comma_corruptions_introduced": [],
            "functional_loss": False,
            "corruption_detected": False
        }
        
        # Compare functions
        current_funcs = {f.name: f for f in current.functions}
        previous_funcs = {f.name: f for f in previous.functions}
        
        for name, func in current_funcs.items():
            if name not in previous_funcs:
                diff["added_functions"].append(name)
            else:
                # Check if function signature changed
                prev_func = previous_funcs[name]
                if (func.args != prev_func.args or 
                    func.kwargs != prev_func.kwargs or 
                    func.return_annotation != prev_func.return_annotation):
                    diff["modified_functions"].append(name)
        
        for name, func in previous_funcs.items():
            if name not in current_funcs:
                diff["removed_functions"].append(name)
                diff["functional_loss"] = True
        
        # Compare classes
        current_classes = {c.name: c for c in current.classes}
        previous_classes = {c.name: c for c in previous.classes}
        
        for name, cls in current_classes.items():
            if name not in previous_classes:
                diff["added_classes"].append(name)
            else:
                # Check if class signature changed
                prev_cls = previous_classes[name]
                if (cls.bases != prev_cls.bases or 
                    len(cls.methods) != len(prev_cls.methods)):
                    diff["modified_classes"].append(name)
                else:
                    # Check if methods changed
                    current_methods = {m.name: m for m in cls.methods}
                    previous_methods = {m.name: m for m in prev_cls.methods}
                    
                    for method_name in current_methods:
                        if method_name not in previous_methods:
                            diff["modified_classes"].append(name)
                            break
                    
                    for method_name in previous_methods:
                        if method_name not in current_methods:
                            diff["modified_classes"].append(name)
                            diff["functional_loss"] = True
                            break
        
        for name, cls in previous_classes.items():
            if name not in current_classes:
                diff["removed_classes"].append(name)
                diff["functional_loss"] = True
        
        # Compare syntax errors
        current_errors = {f"{e[0]}: {e[1]}" for e in current.syntax_errors}
        previous_errors = {f"{e[0]}: {e[1]}" for e in previous.syntax_errors}
        
        diff["syntax_errors_fixed"] = list(previous_errors - current_errors)
        diff["syntax_errors_introduced"] = list(current_errors - previous_errors)
        
        # Compare comma corruptions
        current_corruptions = {f"{c[0]}: {c[1]}" for c in current.comma_corruptions}
        previous_corruptions = {f"{c[0]}: {c[1]}" for c in previous.comma_corruptions}
        
        diff["comma_corruptions_fixed"] = list(previous_corruptions - current_corruptions)
        diff["comma_corruptions_introduced"] = list(current_corruptions - previous_corruptions)
        
        # Check if corruption was detected
        if previous.syntax_errors or previous.comma_corruptions:
            diff["corruption_detected"] = True
        
        return diff
    
    def analyze_commit_pair(self, commit1: str, commit2: str) -> Dict[str, Any]:
        """Analyze differences between two commits."""
        python_files = self.get_python_files()
        results = {
            "commit1": commit1,
            "commit2": commit2,
            "files_analyzed": 0,
            "files_with_corruption": 0,
            "files_with_functional_loss": 0,
            "total_syntax_errors": 0,
            "total_comma_corruptions": 0,
            "file_diffs": []
        }
        
        for file_path in python_files:
            artifact1 = self.analyze_file(file_path, commit1)
            artifact2 = self.analyze_file(file_path, commit2)
            
            if artifact1 and artifact2:
                diff = self.compare_artifacts(artifact1, artifact2)
                results["files_analyzed"] += 1
                
                if diff["corruption_detected"]:
                    results["files_with_corruption"] += 1
                
                if diff["functional_loss"]:
                    results["files_with_functional_loss"] += 1
                
                results["total_syntax_errors"] += len(artifact1.syntax_errors) + len(artifact2.syntax_errors)
                results["total_comma_corruptions"] += len(artifact1.comma_corruptions) + len(artifact2.comma_corruptions)
                
                results["file_diffs"].append(diff)
                
                # Add to RDF model
                self.add_diff_to_model(artifact1, artifact2, diff, commit1, commit2)
        
        return results
    
    def add_diff_to_model(self, artifact1: FileArtifact, artifact2: FileArtifact, 
                         diff: Dict[str, Any], commit1: str, commit2: str) -> None:
        """Add diff information to the RDF model."""
        # Create file nodes
        file1_uri = artifact1.to_rdf(self.graph)
        file2_uri = artifact2.to_rdf(self.graph)
        
        # Create diff node
        diff_uri = URIRef(f"http://example.org/diff/{commit1}_{commit2}/{artifact1.path}")
        self.graph.add((diff_uri, RDF.type, DIFF.FileDiff))
        self.graph.add((diff_uri, DIFF.compares, file1_uri))
        self.graph.add((diff_uri, DIFF.compares, file2_uri))
        self.graph.add((diff_uri, DIFF.fromCommit, Literal(commit1)))
        self.graph.add((diff_uri, DIFF.toCommit, Literal(commit2)))
        
        # Add functional loss information
        if diff["functional_loss"]:
            self.graph.add((diff_uri, DIFF.hasFunctionalLoss, Literal(True)))
            
            # Add details about lost functions
            for func_name in diff["removed_functions"]:
                loss_node = BNode()
                self.graph.add((loss_node, RDF.type, DIFF.FunctionLoss))
                self.graph.add((loss_node, RDFS.label, Literal(f"Lost function: {func_name}")))
                self.graph.add((diff_uri, DIFF.hasLoss, loss_node))
            
            # Add details about lost classes
            for class_name in diff["removed_classes"]:
                loss_node = BNode()
                self.graph.add((loss_node, RDF.type, DIFF.ClassLoss))
                self.graph.add((loss_node, RDFS.label, Literal(f"Lost class: {class_name}")))
                self.graph.add((diff_uri, DIFF.hasLoss, loss_node))
        
        # Add corruption information
        if diff["corruption_detected"]:
            self.graph.add((diff_uri, DIFF.hasCorruption, Literal(True)))
            
            # Add details about syntax errors
            for error in artifact1.syntax_errors:
                error_node = BNode()
                self.graph.add((error_node, RDF.type, CORRUPTION.SyntaxError))
                self.graph.add((error_node, RDFS.label, Literal(f"Line {error[0]}: {error[1]}")))
                self.graph.add((diff_uri, CORRUPTION.hasSyntaxError, error_node))
            
            # Add details about comma corruptions
            for corruption in artifact1.comma_corruptions:
                corruption_node = BNode()
                self.graph.add((corruption_node, RDF.type, CORRUPTION.CommaCorruption))
                self.graph.add((corruption_node, RDFS.label, Literal(f"Line {corruption[0]}: {corruption[1]}")))
                self.graph.add((diff_uri, CORRUPTION.hasCommaCorruption, corruption_node))
    
    def find_corruption_introduction(self, start_commit: str = "HEAD~1", 
                                    target_branch: str = "main") -> Dict[str, Any]:
        """Find when corruption was introduced by searching through commits."""
        logger.info(f"Starting corruption search from {start_commit} towards {target_branch}")
        
        # First check if the start commit has corruption
        start_artifact_results = self.analyze_commit_pair("HEAD", start_commit)
        
        if start_artifact_results["files_with_corruption"] == 0:
            logger.info(f"No corruption found in {start_commit}, checking earlier commits")
            
            # Get the commit history
            result = subprocess.run(
                ["git", "log", "--format=%H", f"{start_commit}..{target_branch}"],
                capture_output=True,
                text=True,
                check=True
            )
            commits = result.stdout.strip().split("\n")
            
            if not commits or commits[0] == '':
                logger.warning(f"No commits found between {start_commit} and {target_branch}")
                return {
                    "corruption_found": False,
                    "message": f"No corruption found between {start_commit} and {target_branch}"
                }
            
            logger.info(f"Found {len(commits)} commits to check")
            
            # Binary search through commits
            left = 0
            right = len(commits) - 1
            corruption_commit = None
            
            while left <= right:
                mid = (left + right) // 2
                mid_commit = commits[mid]
                
                # Check if this commit has corruption
                if mid > 0:
                    prev_commit = commits[mid-1]
                else:
                    prev_commit = target_branch
                
                logger.info(f"Checking commit {mid+1}/{len(commits)}: {mid_commit[:8]}")
                results = self.analyze_commit_pair(prev_commit, mid_commit)
                
                if results["files_with_corruption"] > 0:
                    # Corruption found, check earlier commits
                    corruption_commit = mid_commit
                    right = mid - 1
                else:
                    # No corruption, check later commits
                    left = mid + 1
            
            if corruption_commit:
                # Get commit details
                result = subprocess.run(
                    ["git", "show", "--format=%h %an %ad %s", "--date=short", corruption_commit],
                    capture_output=True,
                    text=True,
                    check=True
                )
                commit_details = result.stdout.split("\n")[0]
                
                return {
                    "corruption_found": True,
                    "commit": corruption_commit,
                    "commit_details": commit_details,
                    "message": f"Corruption introduced in commit: {commit_details}"
                }
            else:
                return {
                    "corruption_found": False,
                    "message": f"No corruption found between {start_commit} and {target_branch}"
                }
        else:
            # Corruption found in the start commit
            return {
                "corruption_found": True,
                "commit": start_commit,
                "message": f"Corruption found in commit {start_commit}"
            }
    
    def analyze_functional_loss(self) -> Dict[str, Any]:
        """Analyze functional loss between HEAD and previous commit."""
        logger.info("Analyzing functional loss between HEAD and previous commit")
        
        results = self.analyze_commit_pair("HEAD", "HEAD~1")
        
        # Summarize functional loss
        loss_summary = {
            "total_files_analyzed": results["files_analyzed"],
            "files_with_functional_loss": results["files_with_functional_loss"],
            "total_functions_lost": sum(len(diff["removed_functions"]) for diff in results["file_diffs"]),
            "total_classes_lost": sum(len(diff["removed_classes"]) for diff in results["file_diffs"]),
            "files_with_loss": []
        }
        
        for diff in results["file_diffs"]:
            if diff["functional_loss"]:
                loss_summary["files_with_loss"].append({
                    "path": diff["path"],
                    "lost_functions": diff["removed_functions"],
                    "lost_classes": diff["removed_classes"]
                })
        
        return loss_summary
    
    def save_model(self, output_path: str = "semantic_diff_model.ttl") -> None:
        """Save the RDF model to a file."""
        self.graph.serialize(destination=output_path, format="turtle")
        logger.info(f"Semantic model saved to {output_path}")
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run the complete analysis."""
        logger.info("Starting semantic diff analysis")
        
        # Check if HEAD~1 has corruption
        corruption_results = self.find_corruption_introduction("HEAD~1", "main")
        
        # Analyze functional loss
        loss_results = self.analyze_functional_loss()
        
        # Save the semantic model
        self.save_model()
        
        # Combine results
        results = {
            "corruption_analysis": corruption_results,
            "functional_loss_analysis": loss_results,
            "model_path": "semantic_diff_model.ttl"
        }
        
        return results

def main():
    """Main function to run the semantic diff analyzer."""
    analyzer = SemanticDiffAnalyzer()
    results = analyzer.run_analysis()
    
    # Print corruption analysis results
    print("\n" + "="*80)
    print("CORRUPTION ANALYSIS RESULTS")
    print("="*80)
    if results["corruption_analysis"]["corruption_found"]:
        print(f"✓ Corruption found: {results['corruption_analysis']['message']}")
    else:
        print(f"✗ No corruption found: {results['corruption_analysis']['message']}")
    
    # Print functional loss analysis results
    print("\n" + "="*80)
    print("FUNCTIONAL LOSS ANALYSIS RESULTS")
    print("="*80)
    loss = results["functional_loss_analysis"]
    print(f"Files analyzed: {loss['total_files_analyzed']}")
    print(f"Files with functional loss: {loss['files_with_functional_loss']}")
    print(f"Total functions lost: {loss['total_functions_lost']}")
    print(f"Total classes lost: {loss['total_classes_lost']}")
    
    if loss["files_with_loss"]:
        print("\nFiles with functional loss:")
        for file_loss in loss["files_with_loss"]:
            print(f"\n{file_loss['path']}:")
            if file_loss["lost_functions"]:
                print("  Lost functions:")
                for func in file_loss["lost_functions"]:
                    print(f"    - {func}")
            if file_loss["lost_classes"]:
                print("  Lost classes:")
                for cls in file_loss["lost_classes"]:
                    print(f"    - {cls}")
    
    print("\n" + "="*80)
    print(f"Semantic model saved to: {results['model_path']}")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
