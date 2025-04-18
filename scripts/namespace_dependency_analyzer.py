#!/usr/bin/env python3
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt

# Configure logging with detailed error monitoring
class ErrorMonitor(logging.Handler):
    def __init__(self):
        super().__init__()
        self.error_count = 0
        self.error_details = []
        self.processing_steps = []
        self.validation_states = []
        self.validation_errors = 0  # Track validation errors separately

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.error_count += 1
            if "Malformed URI" in record.getMessage():
                self.validation_errors += 1
            self.error_details.append({
                'timestamp': datetime.now().isoformat(),
                'level': record.levelname,
                'message': record.getMessage(),
                'step': self.processing_steps[-1] if self.processing_steps else 'unknown'
            })
            logging.error(f"Error #{self.error_count} (Validation: {self.validation_errors}): {record.getMessage()} in step {self.processing_steps[-1] if self.processing_steps else 'unknown'}")

error_monitor = ErrorMonitor()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/namespace_dependency_analyzer.log'),
        logging.StreamHandler(),
        error_monitor
    ]
)

class NamespaceDependencyAnalyzer:
    def __init__(self, inventory_file: str = 'docs/example_org_inventory.md'):
        self.inventory_file = Path(inventory_file)
        self.namespace_pattern = re.compile(r'@prefix\s+(\w+):\s*<([^>]+)>')
        self.python_namespace_pattern = re.compile(r'Namespace\("([^"]+)"\)')
        self.usage_pattern = re.compile(r'(\w+):\w+')
        self.dependencies: Dict[str, Set[str]] = {}
        self.graph = nx.DiGraph()
        self.namespace_usage: Dict[str, Dict[str, int]] = {}
        self.errors: List[str] = []
        self.processing_steps: List[str] = []
        self.validation_errors: int = 0  # Track validation errors in instance

    def log_processing_step(self, step: str) -> None:
        """Log the current processing step for error tracking."""
        self.processing_steps.append(step)
        error_monitor.processing_steps.append(step)
        logging.info(f"Starting processing step: {step}")

    def validate_uri(self, uri: str) -> bool:
        """Validate URI format and log errors."""
        self.log_processing_step("validate_uri")
        if not uri.startswith('http://'):
            error_msg = f"Malformed URI: {uri} - missing double slash"
            self.errors.append(error_msg)
            self.validation_errors += 1
            logging.error(error_msg)
            error_monitor.validation_states.append({
                'uri': uri,
                'valid': False,
                'error': error_msg
            })
            return False
        error_monitor.validation_states.append({
            'uri': uri,
            'valid': True
        })
        return True

    def parse_inventory(self) -> None:
        """Parse the inventory file to extract namespace definitions and usage."""
        try:
            self.log_processing_step("parse_inventory")
            with open(self.inventory_file, 'r', encoding='utf-8') as f:
                current_file = None
                self.dependencies = {}  # Clear any existing dependencies
                self.namespace_usage = {}  # Clear any existing usage
                has_validation_errors = False
                
                # First pass: validate all URIs
                self.log_processing_step("first_pass_validation")
                for line in f:
                    if line.startswith('## '):
                        current_file = line[3:].strip()
                        continue
                    
                    if current_file and line.strip():
                        # Check namespace definitions
                        for prefix, uri in self.namespace_pattern.findall(line):
                            if not self.validate_uri(uri):
                                has_validation_errors = True
                        
                        # Check Python namespace declarations
                        for uri in self.python_namespace_pattern.findall(line):
                            if not self.validate_uri(uri):
                                has_validation_errors = True
                
                # Log validation state
                logging.info(f"Validation complete. Errors found: {has_validation_errors}")
                logging.info(f"Total error count: {error_monitor.error_count}")
                logging.info(f"Validation error count: {self.validation_errors}")
                logging.info(f"Validation states: {error_monitor.validation_states}")
                
                # If any validation errors were found, return without processing
                if has_validation_errors or self.validation_errors > 0:
                    logging.error(f"Validation errors detected ({self.validation_errors} errors), aborting processing")
                    return
                
                # Reset file pointer for second pass
                f.seek(0)
                current_file = None
                
                # Second pass: process valid URIs
                self.log_processing_step("second_pass_processing")
                for line in f:
                    if line.startswith('## '):
                        current_file = line[3:].strip()
                        continue
                    
                    if current_file and line.strip():
                        # Process namespace definitions
                        for prefix, uri in self.namespace_pattern.findall(line):
                            if current_file not in self.dependencies:
                                self.dependencies[current_file] = set()
                            self.dependencies[current_file].add(f"{prefix}:{uri}")
                            self.graph.add_node(f"{prefix}:{uri}")
                            
                            # Track namespace usage
                            if uri not in self.namespace_usage:
                                self.namespace_usage[uri] = {"definitions": 0, "references": 0}
                            self.namespace_usage[uri]["definitions"] += 1
                        
                        # Process Python namespace declarations
                        for uri in self.python_namespace_pattern.findall(line):
                            if current_file not in self.dependencies:
                                self.dependencies[current_file] = set()
                            # Extract prefix from URI
                            prefix = uri.split('/')[-1].split('#')[0]
                            self.dependencies[current_file].add(f"{prefix}:{uri}")
                            self.graph.add_node(f"{prefix}:{uri}")
                            
                            # Track namespace usage
                            if uri not in self.namespace_usage:
                                self.namespace_usage[uri] = {"definitions": 0, "references": 0}
                            self.namespace_usage[uri]["definitions"] += 1
                        
                        # Process namespace usage
                        for prefix in self.usage_pattern.findall(line):
                            if current_file in self.dependencies:
                                for ns in self.dependencies[current_file]:
                                    if ns.startswith(prefix + ':'):
                                        uri = ns.split(':', 1)[1]
                                        if uri not in self.namespace_usage:
                                            self.namespace_usage[uri] = {"definitions": 0, "references": 0}
                                        self.namespace_usage[uri]["references"] += 1
                                        self.graph.add_edge(ns, f"{prefix}:{uri}")
                                        logging.debug(f"Found reference to {uri} in {current_file}")

        except Exception as e:
            logging.error(f"Error parsing inventory file: {str(e)}")
            raise

    def generate_dependency_graph(self) -> None:
        """Generate a visualization of the namespace dependency graph."""
        plt.figure(figsize=(12, 8), facecolor='white')
        ax = plt.gca()
        ax.set_facecolor('white')
        
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, 
                node_color='lightblue',
                node_size=2000, 
                font_size=8,
                font_weight='bold',
                edge_color='#666666',
                width=1.5)
        
        plt.title("Namespace Dependency Graph", pad=20)
        plt.savefig('docs/namespace_dependency_graph.svg', 
                   format='svg',
                   facecolor='white',
                   edgecolor='none',
                   bbox_inches='tight')
        plt.close()

    def generate_analysis_report(self) -> str:
        """Generate a detailed analysis report of namespace dependencies."""
        report = []
        report.append("# Namespace Dependency Analysis Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        # Summary Statistics
        report.append("## Summary Statistics")
        report.append(f"- Total namespaces: {len(self.namespace_usage)}")
        report.append(f"- Total files with namespace definitions: {len(self.dependencies)}")
        if self.errors:
            report.append("\n## Errors Detected")
            for error in self.errors:
                report.append(f"- {error}")
        report.append("")

        # Namespace Usage Analysis
        report.append("## Namespace Usage Analysis")
        for uri, usage in sorted(self.namespace_usage.items()):
            report.append(f"### {uri}")
            report.append(f"- Definitions: {usage['definitions']}")
            report.append(f"- References: {usage['references']}")
            if usage['definitions'] > 0 and usage['references'] == 0:
                report.append("- WARNING: This namespace is defined but never referenced")
            report.append("")

        # Dependency Analysis
        report.append("## Dependency Analysis")
        for file, namespaces in sorted(self.dependencies.items()):
            report.append(f"### {file}")
            for ns in sorted(namespaces):
                report.append(f"- {ns}")
            report.append("")

        return "\n".join(report)

    def save_analysis_report(self, output_file: str = 'docs/namespace_dependency_analysis.md') -> None:
        """Save the analysis report to a file."""
        report = self.generate_analysis_report()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logging.info(f"Analysis report saved to {output_file}")

def main() -> None:
    """Main function to run the namespace dependency analyzer."""
    analyzer = NamespaceDependencyAnalyzer()
    logging.info("Starting namespace dependency analysis...")
    analyzer.parse_inventory()
    analyzer.generate_dependency_graph()
    analyzer.save_analysis_report()
    logging.info("Namespace dependency analysis complete.")

if __name__ == "__main__":
    main() 