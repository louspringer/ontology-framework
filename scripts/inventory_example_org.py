#!/usr/bin/env python3
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from ontology_framework.config.logging_config import setup_logging, get_logger

# Set up logging
logger = get_logger(__name__)

class ExampleOrgInventory:
    def __init__(self, root_dir: str = '.'):
        self.root_dir = Path(root_dir)
        self.results: Dict[str, List[Tuple[int, str]]] = {}
        # Match example.org in any context
        self.pattern = re.compile(r'example\.org')
        self.supported_extensions = {'.ttl', '.py', '.md'}

    def scan_file(self, file_path: Path) -> None:
        """Scan a single file for example.org usage."""
        try:
            # Skip binary files
            if not self._is_text_file(file_path):
                logger.debug(f"Skipping binary file: {file_path}")
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if self.pattern.search(line):
                        if str(file_path) not in self.results:
                            self.results[str(file_path)] = []
                        self.results[str(file_path)].append((i, line.strip()))
        except UnicodeDecodeError:
            logger.warning(f"Could not decode file {file_path} as UTF-8")
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {str(e)}")

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if a file is a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Try to read first 1KB
            return True
        except UnicodeDecodeError:
            return False

    def scan_directory(self) -> None:
        """Scan all files in the directory for example.org usage."""
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.supported_extensions:
                self.scan_file(file_path)

    def generate_report(self) -> str:
        """Generate a report of all example.org usage."""
        report = []
        report.append("# Example.org Usage Inventory")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        if not self.results:
            report.append("No example.org usage found.")
            return "\n".join(report)

        for file_path, occurrences in sorted(self.results.items()):
            report.append(f"## {file_path}")
            for line_num, line in occurrences:
                report.append(f"Line {line_num}: {line}")
            report.append("")

        return "\n".join(report)

    def save_report(self, output_file: str = 'docs/example_org_inventory.md') -> None:
        """Save the inventory report to a file."""
        try:
            report = self.generate_report()
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving report to {output_file}: {str(e)}")
            raise

def main():
    # Set up logging before starting
    setup_logging('example_org_inventory.log')
    
    inventory = ExampleOrgInventory()
    logger.info("Starting example.org usage inventory...")
    inventory.scan_directory()
    inventory.save_report()
    logger.info("Inventory complete.")

if __name__ == "__main__":
    main() 