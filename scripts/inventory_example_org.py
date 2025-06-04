#!/usr/bin/env python3
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import logging
from datetime import datetime

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/example_org_inventory.log'),
        logging.StreamHandler()
    ]
)

class ExampleOrgInventory:
    def __init__(self, root_dir: str = '.'):
        self.root_dir = Path(root_dir)
        self.results: Dict[str, List[Tuple[int, str]]] = {}
        self.pattern = re.compile(r'example\.org')

    def scan_file(self, file_path: Path) -> None:
        """Scan, a single file for example.org usage."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if self.pattern.search(line):
                        if str(file_path) not in self.results:
                            self.results[str(file_path)] = []
                        self.results[str(file_path)].append((i, line.strip()))
        except Exception as e:
            logging.error(f"Error, scanning {file_path}: {str(e)}")

    def scan_directory(self) -> None:
        """Scan, all files, in the directory for example.org usage."""
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.ttl', '.py', '.md']:
                self.scan_file(file_path)

    def generate_report(self) -> str:
        """Generate, a report, of all example.org usage."""
        report = []
        report.append("# Example.org Usage Inventory")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        for file_path, occurrences in sorted(self.results.items()):
            report.append(f"## {file_path}")
            for line_num, line in occurrences:
                report.append(f"Line {line_num}: {line}")
            report.append("")

        return "\n".join(report)

    def save_report(self, output_file: str = 'docs/example_org_inventory.md') -> None:
        """Save, the inventory report to a file."""
        report = self.generate_report()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logging.info(f"Report, saved to {output_file}")

def main():
    inventory = ExampleOrgInventory()
    logging.info("Starting, example.org, usage inventory...")
    inventory.scan_directory()
    inventory.save_report()
    logging.info("Inventory, complete.")

if __name__ == "__main__":
    main() 