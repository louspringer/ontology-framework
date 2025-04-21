"""
Code analyzer for detecting anti-patterns in Python files.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import re
from dataclasses import dataclass
from enum import Enum, auto

class IssueType(Enum):
    """Types of issues that can be detected."""
    REGEX_STRING = auto()
    RDF_STRING = auto()
    TURTLE_STRING = auto()
    MISSING_TYPE_HINTS = auto()

@dataclass
class CodeIssue:
    """Represents a detected code issue."""
    file_path: Path
    line_number: int
    issue_type: IssueType
    description: str
    code_snippet: str

class CodeAnalyzer:
    """Analyzes Python code for common anti-patterns."""
    
    def __init__(self):
        self.issues: List[CodeIssue] = []
        self.regex_patterns = {
            r're\.(?:compile|match|search|findall|finditer|sub|split)\([\'\"].*[\'\"]\)': 
                "Raw regex string pattern",
            r'@prefix\s+\w+\s*:\s*<.*>': 
                "Direct Turtle prefix declaration",
            r'\.write_text\(.*\)': 
                "Direct file writing without graph serialization",
            r'def\s+\w+\([^:]*\)(?!\s*->)': 
                "Function missing return type annotation"
        }
        
    def analyze_file(self, file_path: Path) -> List[CodeIssue]:
        """Analyze a single Python file for anti-patterns."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            # Check for regex patterns
            self._check_regex_patterns(file_path, content)
            
            # Check for RDF/Turtle string manipulation
            self._check_rdf_patterns(file_path, content)
            
            # Check for missing type hints
            self._check_type_hints(file_path, tree)
            
            return self.issues
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return []
    
    def _check_regex_patterns(self, file_path: Path, content: str) -> None:
        """Check for raw regex string patterns."""
        for pattern, description in self.regex_patterns.items():
            for match in re.finditer(pattern, content):
                line_number = content[:match.start()].count('\n') + 1
                self.issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_number,
                    issue_type=IssueType.REGEX_STRING,
                    description=description,
                    code_snippet=match.group(0)
                ))
    
    def _check_rdf_patterns(self, file_path: Path, content: str) -> None:
        """Check for RDF/Turtle string manipulation."""
        turtle_patterns = [
            r'@prefix\s+\w+\s*:\s*<.*>',
            r'\.write_text\(.*\)',
            r'\.read_text\(.*\)'
        ]
        
        for pattern in turtle_patterns:
            for match in re.finditer(pattern, content):
                line_number = content[:match.start()].count('\n') + 1
                self.issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=line_number,
                    issue_type=IssueType.TURTLE_STRING,
                    description="Direct Turtle/RDF string manipulation",
                    code_snippet=match.group(0)
                ))
    
    def _check_type_hints(self, file_path: Path, tree: ast.AST) -> None:
        """Check for missing type hints in function definitions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.returns:
                    self.issues.append(CodeIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        issue_type=IssueType.MISSING_TYPE_HINTS,
                        description="Function missing return type annotation",
                        code_snippet=ast.get_source_segment(tree, node)
                    ))

def analyze_directory(directory: Path) -> Dict[str, List[CodeIssue]]:
    """Analyze all Python files in a directory."""
    analyzer = CodeAnalyzer()
    results: Dict[str, List[CodeIssue]] = {}
    
    for file_path in directory.rglob("*.py"):
        issues = analyzer.analyze_file(file_path)
        if issues:
            results[str(file_path)] = issues
    
    return results

def print_analysis_results(results: Dict[str, List[CodeIssue]]) -> None:
    """Print analysis results in a readable format."""
    for file_path, issues in results.items():
        print(f"\nFile: {file_path}")
        for issue in issues:
            print(f"  Line {issue.line_number}: {issue.issue_type.name}")
            print(f"    Description: {issue.description}")
            print(f"    Code: {issue.code_snippet}")
            print()

if __name__ == "__main__":
    # Example usage
    project_root = Path(__file__).parent.parent
    results = analyze_directory(project_root)
    print_analysis_results(results) 