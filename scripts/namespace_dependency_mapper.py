#!/usr/bin/env python3
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from ontology_framework.config.logging_config import setup_logging, get_logger

# Set up logging
logger = get_logger(__name__)

class NamespaceDependencyMapper:
    def __init__(self, inventory_file: str = 'docs/example_org_inventory.md'):
        self.inventory_file = Path(inventory_file)
        self.namespace_pattern = re.compile(r'@prefix\s+(\w+):\s*<([^>]+)>')
        self.python_namespace_pattern = re.compile(r'Namespace\("([^"]+)"\)')
        self.usage_pattern = re.compile(r'(\w+):\w+')
        self.dependencies: Dict[str, Set[str]] = {}
        self.graph = nx.DiGraph()

    def parse_inventory(self) -> None:
        """Parse the inventory file to extract namespace definitions and usage."""
        try:
            if not self.inventory_file.exists():
                logger.warning(f"Inventory file {self.inventory_file} does not exist")
                return
                
            with open(self.inventory_file, 'r', encoding='utf-8') as f:
                current_file = None
                for line in f:
                    if line.startswith('## '):
                        current_file = line[3:].strip()
                        continue
                    if current_file and line.strip():
                        # Extract namespace definitions
                        for prefix, uri in self.namespace_pattern.findall(line):
                            if current_file not in self.dependencies:
                                self.dependencies[current_file] = set()
                            namespace = f"{prefix}:{uri}"
                            self.dependencies[current_file].add(namespace)
                            self.graph.add_node(namespace)
                        
                        # Extract Python namespace declarations
                        for uri in self.python_namespace_pattern.findall(line):
                            if current_file not in self.dependencies:
                                self.dependencies[current_file] = set()
                            # Extract prefix from URI
                            prefix = uri.split('/')[-1].split('#')[0]
                            namespace = f"{prefix}:{uri}"
                            self.dependencies[current_file].add(namespace)
                            self.graph.add_node(namespace)
                        
                        # Extract namespace usage
                        for prefix in self.usage_pattern.findall(line):
                            if current_file in self.dependencies:
                                # Find the namespace definition for this prefix
                                for namespace in self.dependencies[current_file]:
                                    if namespace.startswith(prefix + ':'):
                                        # Add edge from the namespace to itself (self-reference)
                                        self.graph.add_edge(namespace, namespace)

        except Exception as e:
            logger.error(f"Error parsing inventory file: {str(e)}")
            raise  # Re-raise the exception to ensure proper error handling

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

    def generate_migration_plan(self) -> str:
        """Generate a migration plan based on namespace dependencies."""
        plan = []
        plan.append("# Namespace Migration Plan")
        plan.append(f"Generated: {datetime.now().isoformat()}")
        plan.append("")

        # Group namespaces by type
        ontology_ns = set()
        python_ns = set()
        doc_ns = set()

        for file, namespaces in self.dependencies.items():
            if file.endswith('.ttl'):
                ontology_ns.update(namespaces)
            elif file.endswith('.py'):
                python_ns.update(namespaces)
            elif file.endswith('.md'):
                doc_ns.update(namespaces)

        # Generate migration steps
        plan.append("## Migration Steps")
        plan.append("")

        plan.append("## 1. Ontology Namespaces")
        for ns in sorted(ontology_ns):
            prefix, uri = ns.split(':', 1)
            plan.append(f"- Migrate `{prefix}` from `{uri}` to `https://ontologies.louspringer.com/test/`")

        plan.append("\n## 2. Python Namespaces")
        for ns in sorted(python_ns):
            prefix, uri = ns.split(':', 1)
            plan.append(f"- Update `{prefix}` in Python scripts from `{uri}` to `https://ontologies.louspringer.com/test/`")

        plan.append("\n## 3. Documentation References")
        for ns in sorted(doc_ns):
            prefix, uri = ns.split(':', 1)
            plan.append(f"- Update `{prefix}` in documentation from `{uri}` to `https://ontologies.louspringer.com/test/`")

        return "\n".join(plan)

    def save_migration_plan(self, output_file: str = 'docs/namespace_migration_plan.md') -> None:
        """Save the migration plan to a file."""
        plan = self.generate_migration_plan()
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(plan)
        logger.info(f"Migration plan saved to {output_file}")

def main() -> None:
    """Main function to run the namespace dependency mapper."""
    # Set up logging before starting
    setup_logging('namespace_dependency_mapper.log')
    
    mapper = NamespaceDependencyMapper()
    logger.info("Starting namespace dependency mapping...")
    mapper.parse_inventory()
    mapper.generate_dependency_graph()
    mapper.save_migration_plan()
    logger.info("Namespace dependency mapping complete.")

if __name__ == "__main__":
    main() 