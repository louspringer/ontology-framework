#!/usr/bin/env python3
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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
        self.validation_errors: int = 0

    def get_dependencies(self) -> nx.DiGraph:
        """Return the dependency graph."""
        return self.graph

    def analyze(self, graph) -> nx.DiGraph:
        """Analyze dependencies from an RDF graph."""
        if not hasattr(graph, 'triples'):
            raise ValueError("Input must be an RDF graph")
        
        # Clear previous analysis
        self.graph = nx.DiGraph()
        
        # Track namespace to URI mappings
        namespace_map = {}
        
        # Extract namespaces and track dependencies
        for subject, predicate, obj in graph:
            # Extract namespace from subject
            if hasattr(subject, 'toPython'):
                subject_str = subject.toPython()
            else:
                subject_str = str(subject)
            
            # Extract namespace from object if it's a URI
            if hasattr(obj, 'toPython'):
                obj_str = obj.toPython()
            else:
                obj_str = str(obj)
            
            # Find subject namespace
            subject_ns = None
            if '#' in subject_str:
                subject_ns = subject_str.split('#')[0] + '#'
            elif '/' in subject_str:
                # Handle URIs without fragment identifiers
                parts = subject_str.rstrip('/').split('/')
                if len(parts) > 3:  # Skip protocol and domain
                    subject_ns = '/'.join(parts[:-1]) + '/'
                    
            # Find object namespace  
            obj_ns = None
            if '#' in obj_str:
                obj_ns = obj_str.split('#')[0] + '#'
            elif '/' in obj_str:
                parts = obj_str.rstrip('/').split('/')
                if len(parts) > 3:
                    obj_ns = '/'.join(parts[:-1]) + '/'
            
            # Add namespaces to graph
            if subject_ns:
                self.graph.add_node(subject_ns)
                namespace_map[subject_ns] = subject_ns
            if obj_ns:
                self.graph.add_node(obj_ns)
                namespace_map[obj_ns] = obj_ns
                
            # Create dependency edge if both namespaces exist and are different
            if subject_ns and obj_ns and subject_ns != obj_ns:
                self.graph.add_edge(subject_ns, obj_ns)
        
        return self.graph

    def get_direct_dependencies(self, namespace: str) -> List[str]:
        """Get direct dependencies of a namespace."""
        if namespace in self.graph:
            return list(self.graph.successors(namespace))
        return []

    def get_transitive_dependencies(self, namespace: str) -> List[str]:
        """Get transitive dependencies of a namespace."""
        if namespace not in self.graph:
            return []
        
        transitive = set()
        # BFS to find all reachable nodes
        visited = set()
        queue = [namespace]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            for successor in self.graph.successors(current):
                if successor != namespace:  # Avoid self-reference
                    transitive.add(successor)
                    queue.append(successor)
        
        return list(transitive)

    def get_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies."""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []

    def generate_report(self) -> Dict:
        """Generate a dependency report."""
        return {
            "namespaces": list(self.graph.nodes()),
            "direct_dependencies": {
                node: self.get_direct_dependencies(node) 
                for node in self.graph.nodes()
            },
            "transitive_dependencies": {
                node: self.get_transitive_dependencies(node) 
                for node in self.graph.nodes()
            },
            "circular_dependencies": self.get_circular_dependencies()
        }

    def log_processing_step(self, step: str) -> None:
        """Log the current processing step for error tracking."""
        self.processing_steps.append(step)
        logging.info(f"Starting processing step: {step}")

    def validate_uri(self, uri: str) -> bool:
        """Validate URI format and log errors."""
        self.log_processing_step("validate_uri")
        if not uri.startswith('http://') and not uri.startswith('https://'):
            error_msg = f"Malformed URI: {uri} - missing protocol"
            self.errors.append(error_msg)
            self.validation_errors += 1
            logging.error(error_msg)
            return False
        return True

    def parse_inventory(self) -> None:
        """Parse the inventory file to extract namespace definitions and usage."""
        try:
            self.log_processing_step("parse_inventory")
            if not self.inventory_file.exists():
                logging.warning(f"Inventory file {self.inventory_file} does not exist")
                return
                
            with open(self.inventory_file, 'r', encoding='utf-8') as f:
                current_file = None
                self.dependencies = {}
                self.namespace_usage = {}
                
                for line in f:
                    if line.startswith('## '):
                        current_file = line[3:].strip()
                        continue
                        
                    if current_file and line.strip():
                        # Check namespace definitions
                        for prefix, uri in self.namespace_pattern.findall(line):
                            if self.validate_uri(uri):
                                if current_file not in self.dependencies:
                                    self.dependencies[current_file] = set()
                                self.dependencies[current_file].add(f"{prefix}:{uri}")
                                self.graph.add_node(f"{prefix}:{uri}")
                                
                                if uri not in self.namespace_usage:
                                    self.namespace_usage[uri] = {"definitions": 0, "references": 0}
                                self.namespace_usage[uri]["definitions"] += 1

        except Exception as e:
            logging.error(f"Error parsing inventory file: {str(e)}")
            raise

    def generate_dependency_graph(self) -> None:
        """Generate a visualization of the namespace dependency graph."""
        plt.figure(figsize=(12, 8), facecolor='white')
        ax = plt.gca()
        ax.set_facecolor('white')
        
        if len(self.graph.nodes()) > 0:
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
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
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