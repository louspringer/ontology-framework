#!/usr/bin/env python3
"""Script to find all files using example.org."""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from rdflib import Graph, URIRef
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExampleOrgFinder:
    """Finds files using example.org in the codebase."""
    
    def __init__(self, root_dir: str = "."):
        """Initialize the finder with root directory."""
        self.root_dir = Path(root_dir)
        self.example_org_pattern = re.compile(r'example\.org', re.IGNORECASE)
        self.results: List[Dict[str, str]] = []
        
    def find_in_file(self, file_path: Path) -> List[Tuple[int, str]]:
        """Find example.org usage in a single file."""
        matches = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if self.example_org_pattern.search(line):
                        matches.append((i, line.strip()))
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
        return matches
    
    def find_in_rdf(self, file_path: Path) -> List[Tuple[int, str]]:
        """Find example.org usage in RDF files."""
        matches = []
        try:
            g = Graph()
            g.parse(file_path)
            for s, p, o in g:
                if isinstance(s, URIRef) and 'example.org' in str(s):
                    matches.append((0, f"Subject: {s}"))
                if isinstance(p, URIRef) and 'example.org' in str(p):
                    matches.append((0, f"Predicate: {p}"))
                if isinstance(o, URIRef) and 'example.org' in str(o):
                    matches.append((0, f"Object: {o}"))
        except Exception as e:
            logger.error(f"Error parsing RDF {file_path}: {e}")
        return matches
    
    def scan_directory(self) -> None:
        """Scan the directory for files using example.org."""
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in ['.py', '.ttl', '.rdf', '.owl', '.n3']:
                    matches = []
                    if file_path.suffix in ['.ttl', '.rdf', '.owl', '.n3']:
                        matches = self.find_in_rdf(file_path)
                    else:
                        matches = self.find_in_file(file_path)
                    
                    if matches:
                        self.results.append({
                            'file': str(file_path),
                            'matches': matches
                        })
                        logger.info(f"Found example.org usage in {file_path}")
    
    def generate_report(self) -> str:
        """Generate a report of findings."""
        report = ["Example.org Usage Report", "=" * 50, ""]
        
        for result in self.results:
            report.append(f"File: {result['file']}")
            for line_num, line in result['matches']:
                if line_num > 0:
                    report.append(f"  Line {line_num}: {line}")
                else:
                    report.append(f"  {line}")
            report.append("")
        
        return "\n".join(report)

def main():
    """Main function."""
    finder = ExampleOrgFinder()
    logger.info("Starting scan for example.org usage...")
    finder.scan_directory()
    
    report = finder.generate_report()
    print(report)
    
    # Save report to file
    with open("example_org_usage_report.txt", "w") as f:
        f.write(report)
    
    logger.info(f"Found {len(finder.results)} files using example.org")
    logger.info("Report saved to example_org_usage_report.txt")

if __name__ == "__main__":
    main() 