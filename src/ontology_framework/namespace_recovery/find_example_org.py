"""Module for finding example.org references in files.

This module provides functionality to scan files and directories for references to
example.org domains that should be replaced with proper namespaces.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

@dataclass
class ExampleOrgReference:
    """Represents a reference to example.org found in a file."""
    file_path: str
    line_number: int
    line_content: str
    context: str  # The type of file or context where it was found

class ExampleOrgFinder:
    """Class for finding example.org references in files and directories."""

    def __init__(self, ignore_patterns: Optional[List[str]] = None):
        """Initialize the finder.
        
        Args:
            ignore_patterns: List of glob patterns to ignore
        """
        self.ignore_patterns = ignore_patterns or []
        self._example_org_pattern = re.compile(r'example\.org', re.IGNORECASE)
        
    def _should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored based on ignore patterns.
        
        Args:
            path: Path to check
        
        Returns:
            True if path should be ignored, False otherwise
        """
        from fnmatch import fnmatch
        return any(fnmatch(path, pattern) for pattern in self.ignore_patterns)

    def scan_file(self, file_path: str) -> List[ExampleOrgReference]:
        """Scan a single file for example.org references.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            List of ExampleOrgReference objects
        """
        if self._should_ignore(file_path):
            return []
            
        references = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if self._example_org_pattern.search(line):
                        context = self._determine_context(file_path)
                        ref = ExampleOrgReference(
                            file_path=file_path,
                            line_number=i,
                            line_content=line.strip(),
                            context=context
                        )
                        references.append(ref)
        except UnicodeDecodeError:
            # Skip binary files
            pass
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
            
        return references

    def scan_directory(self, directory: str) -> List[ExampleOrgReference]:
        """Recursively scan a directory for example.org references.
        
        Args:
            directory: Path to the directory to scan
            
        Returns:
            List of ExampleOrgReference objects
        """
        references = []
        for root, _, files in os.walk(directory):
            if self._should_ignore(root):
                continue
            for file in files:
                if self._should_ignore(file):
                    continue
                file_path = os.path.join(root, file)
                references.extend(self.scan_file(file_path))
                
        return references

    def _determine_context(self, file_path: str) -> str:
        """Determine the context of a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Context string describing the file type
        """
        ext = Path(file_path).suffix.lower()
        contexts = {
            '.ttl': 'Turtle RDF',
            '.rdf': 'RDF/XML',
            '.owl': 'OWL Ontology',
            '.py': 'Python Source',
            '.java': 'Java Source',
            '.js': 'JavaScript',
            '.json': 'JSON',
            '.xml': 'XML',
            '.md': 'Markdown',
            '.txt': 'Text'
        }
        return contexts.get(ext, 'Unknown')

    def generate_report(self, references: List[ExampleOrgReference]) -> Dict[str, Any]:
        """Generate a report from the found references.
        
        Args:
            references: List of ExampleOrgReference objects
            
        Returns:
            Dictionary containing the report data
        """
        contexts: Dict[str, int] = {}
        files: Set[str] = set()
        total_references = len(references)
        
        for ref in references:
            contexts[ref.context] = contexts.get(ref.context, 0) + 1
            files.add(ref.file_path)
            
        return {
            "total_references": total_references,
            "unique_files": len(files),
            "contexts": contexts,
            "references": [
                {
                    "file": ref.file_path,
                    "line": ref.line_number,
                    "content": ref.line_content,
                    "context": ref.context
                }
                for ref in references
            ]
        } 