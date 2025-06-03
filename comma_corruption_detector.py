#!/usr/bin/env python3
# Comma Corruption Detector
#
# This script analyzes Python files to detect comma corruption patterns
# and compares files between Git branches to identify functional loss.
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
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("comma-corruption-detector")

@dataclass
class FunctionSignature:
    """Represents a function signature for semantic comparison."""
    name: str
    args: List[str] = field(default_factory=list)
    lineno: int = 0

@dataclass
class ClassSignature:
    """Represents a class signature for semantic comparison."""
    name: str
    bases: List[str] = field(default_factory=list)
    methods: List[FunctionSignature] = field(default_factory=list)
    lineno: int = 0

@dataclass
class CommaCorruption:
    """Represents a comma corruption in the code."""
    message: str
    lineno: int
    line: str

@dataclass
class FileArtifact:
    """Represents a Python file artifact for semantic comparison."""
    path: str
    functions: List[FunctionSignature] = field(default_factory=list)
    classes: List[ClassSignature] = field(default_factory=list)
    comma_corruptions: List[CommaCorruption] = field(default_factory=list)

class CommaCorruptionDetector:
    """Detects comma corruption in Python files and compares files between branches."""
    
    def __init__(self):
        """Initialize the comma corruption detector."""
        self.current_branch = self.get_current_branch()
        logger.info(f"Current branch: {self.current_branch}")
    
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
    
    def detect_comma_corruption(self, content: str) -> List[CommaCorruption]:
        """Detect comma corruption in Python code."""
        corruptions = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            # Check for misplaced commas
            if "," in line:
                # Check for commas in unusual places
                if line.strip().startswith(",") and not line.strip().startswith(",,"):
                    corruptions.append(CommaCorruption(
                        message=f"Line starts with comma",
                        lineno=i+1,
                        line=line
                    ))
                
                # Check for commas after keywords
                for keyword in ["def", "class", "import", "from", "return", "if", "elif", "else", "for", "while"]:
                    if f"{keyword} ," in line or f"{keyword}," in line:
                        corruptions.append(CommaCorruption(
                            message=f"Comma after keyword '{keyword}'",
                            lineno=i+1,
                            line=line
                        ))
                
                # Check for commas in function calls with no arguments
                if "( ," in line or "(," in line:
                    corruptions.append(CommaCorruption(
                        message=f"Comma after opening parenthesis",
                        lineno=i+1,
                        line=line
                    ))
                
                # Check for double commas
                if ",," in line:
                    corruptions.append(CommaCorruption(
                        message=f"Double comma",
                        lineno=i+1,
                        line=line
                    ))
        
        return corruptions
    
    def extract_functions_and_classes(self, content: str) -> Tuple[List[FunctionSignature], List[ClassSignature]]:
        """Extract function and class signatures from Python code."""
        functions = []
        classes = []
        
        try:
            tree = ast.parse(content)
            
            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # Skip methods (they'll be handled with classes)
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in parent.body):
                        args = [arg.arg for arg in node.args.args]
                        
                        function = FunctionSignature(
                            name=node.name,
                            args=args,
                            lineno=node.lineno
                        )
                        functions.append(function)
            
            # Extract classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Get base classes
                    bases = []
                    for base in node.bases:
                        try:
                            bases.append(ast.unparse(base))
                        except AttributeError:
                            bases.append(str(base))
                    
                    # Get methods
                    methods = []
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef) or isinstance(child, ast.AsyncFunctionDef):
                            method_args = []
                            for arg in child.args.args:
                                if arg.arg != "self" and arg.arg != "cls":
                                    method_args.append(arg.arg)
                            
                            method = FunctionSignature(
                                name=child.name,
                                args=method_args,
                                lineno=child.lineno
                            )
                            methods.append(method)
                    
                    class_sig = ClassSignature(
                        name=node.name,
                        bases=bases,
                        methods=methods,
                        lineno=node.lineno
                    )
                    classes.append(class_sig)
        except SyntaxError:
            # Fall back to regex-based extraction for corrupted files
            functions = self.extract_functions_regex(content)
            classes = self.extract_classes_regex(content)
        except Exception as e:
            logger.error(f"Error extracting functions and classes: {e}")
            # Fall back to regex-based extraction
            functions = self.extract_functions_regex(content)
            classes = self.extract_classes_regex(content)
        
        return functions, classes
    
    def extract_functions_regex(self, content: str) -> List[FunctionSignature]:
        """Extract function signatures using regex (fallback for corrupted files)."""
        functions = []
        function_pattern = r'^\s*def\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)'
        
        for i, line in enumerate(content.split('\n')):
            match = re.match(function_pattern, line)
            if match:
                func_name = match.group(1)
                args_str = match.group(2)
                
                # Parse arguments
                args = []
                if args_str:
                    args = [a.strip() for a in args_str.split(',')]
                
                functions.append(FunctionSignature(
                    name=func_name,
                    args=args,
                    lineno=i+1
                ))
        
        return functions
    
    def extract_classes_regex(self, content: str) -> List[ClassSignature]:
        """Extract class signatures using regex (fallback for corrupted files)."""
        classes = []
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
                
                classes.append(ClassSignature(
                    name=class_name,
                    bases=bases,
                    lineno=i+1
                ))
        
        return classes
    
    def analyze_file(self, file_path: str, commit: str = "HEAD") -> Optional[FileArtifact]:
        """Analyze a Python file at a specific commit."""
        content = self.get_file_content(file_path, commit)
        if not content:
            return None
        
        logger.info(f"Analyzing file {file_path} at commit {commit}")
        
        # Detect comma corruptions
        comma_corruptions = self.detect_comma_corruption(content)
        
        # Extract functions and classes
        functions, classes = self.extract_functions_and_classes(content)
        
        # Create file artifact
        artifact = FileArtifact(
            path=file_path,
            functions=functions,
            classes=classes,
            comma_corruptions=comma_corruptions
        )
        
        logger.info(
            f"Analysis complete for {file_path}: "
            f"{len(functions)} functions, {len(classes)} classes, "
            f"{len(comma_corruptions)} comma corruptions"
        )
        
        return artifact
    
    def compare_artifacts(self, current: FileArtifact, previous: FileArtifact) -> Dict[str, Any]:
        """Compare two file artifacts and identify differences."""
        diff = {
            "path": current.path,
            "added_functions": [],
            "removed_functions": [],
            "added_classes": [],
            "removed_classes": [],
            "comma_corruptions": current.comma_corruptions,
            "functional_loss": False
        }
        
        # Compare functions
        current_funcs = {f.name for f in current.functions}
        previous_funcs = {f.name for f in previous.functions}
        
        diff["added_functions"] = list(current_funcs - previous_funcs)
        diff["removed_functions"] = list(previous_funcs - current_funcs)
        
        if diff["removed_functions"]:
            diff["functional_loss"] = True
        
        # Compare classes
        current_classes = {c.name for c in current.classes}
        previous_classes = {c.name for c in previous.classes}
        
        diff["added_classes"] = list(current_classes - previous_classes)
        diff["removed_classes"] = list(previous_classes - current_classes)
        
        if diff["removed_classes"]:
            diff["functional_loss"] = True
        
        # Compare methods in classes that exist in both versions
        for current_class in current.classes:
            if current_class.name in previous_classes:
                previous_class = next(c for c in previous.classes if c.name == current_class.name)
                
                current_methods = {m.name for m in current_class.methods}
                previous_methods = {m.name for m in previous_class.methods}
                
                removed_methods = previous_methods - current_methods
                if removed_methods:
                    diff["functional_loss"] = True
                    diff.setdefault("removed_methods", {})[current_class.name] = list(removed_methods)
        
        return diff
    
    def analyze_branch_diff(self, target_branch: str = "main") -> List[Dict[str, Any]]:
        """Analyze differences between current branch and target branch."""
        logger.info(f"Comparing current branch '{self.current_branch}' with '{target_branch}'")
        
        # Get Python files in current branch
        python_files = self.get_python_files()
        logger.info(f"Found {len(python_files)} Python files")
        
        results = []
        for file_path in python_files:
            # Analyze file in current branch
            current_artifact = self.analyze_file(file_path, "HEAD")
            if not current_artifact:
                continue
            
            # Analyze file in target branch
            previous_artifact = self.analyze_file(file_path, target_branch)
            if not previous_artifact:
                # File doesn't exist in target branch, it's a new file
                results.append({
                    "path": file_path,
                    "status": "new_file",
                    "comma_corruptions": current_artifact.comma_corruptions,
                    "functions": [f.name for f in current_artifact.functions],
                    "classes": [c.name for c in current_artifact.classes]
                })
                continue
            
            # Compare artifacts
            diff = self.compare_artifacts(current_artifact, previous_artifact)
            results.append(diff)
        
        return results

def main():
    """Main function to run the comma corruption detector."""
    detector = CommaCorruptionDetector()
    
    # Parse command line arguments
    target_branch = "main"
    if len(sys.argv) > 1:
        target_branch = sys.argv[1]
    
    # Analyze differences between branches
    results = detector.analyze_branch_diff(target_branch)
    
    # Print summary
    print("\n=== Comma Corruption and Functional Loss Analysis ===\n")
    
    files_with_corruptions = [r for r in results if r.get("comma_corruptions")]
    files_with_loss = [r for r in results if r.get("functional_loss")]
    
    print(f"Analyzed {len(results)} Python files")
    print(f"Found {len(files_with_corruptions)} files with comma corruptions")
    print(f"Found {len(files_with_loss)} files with functional loss")
    
    # Print detailed results for files with corruptions
    if files_with_corruptions:
        print("\n=== Files with Comma Corruptions ===\n")
        for result in files_with_corruptions:
            print(f"File: {result['path']}")
            for corruption in result.get("comma_corruptions", []):
                print(f"  Line {corruption.lineno}: {corruption.message}")
                print(f"    {corruption.line.strip()}")
            print()
    
    # Print detailed results for files with functional loss
    if files_with_loss:
        print("\n=== Files with Functional Loss ===\n")
        for result in files_with_loss:
            print(f"File: {result['path']}")
            
            if result.get("removed_functions"):
                print("  Removed functions:")
                for func in result["removed_functions"]:
                    print(f"    - {func}")
            
            if result.get("removed_classes"):
                print("  Removed classes:")
                for cls in result["removed_classes"]:
                    print(f"    - {cls}")
            
            if result.get("removed_methods"):
                print("  Removed methods:")
                for cls, methods in result["removed_methods"].items():
                    for method in methods:
                        print(f"    - {cls}.{method}")
            
            print()
    
    # Save results to JSON file
    with open("comma_corruption_analysis.json", "w") as f:
        # Convert dataclasses to dictionaries
        serializable_results = []
        for result in results:
            serializable_result = dict(result)
            if "comma_corruptions" in serializable_result:
                serializable_result["comma_corruptions"] = [
                    {
                        "message": c.message,
                        "lineno": c.lineno,
                        "line": c.line
                    }
                    for c in serializable_result["comma_corruptions"]
                ]
            serializable_results.append(serializable_result)
        
        json.dump(serializable_results, f, indent=2)
    
    print(f"Results saved to comma_corruption_analysis.json")

if __name__ == "__main__":
    main()
