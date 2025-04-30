"""Visualization module for dependency graphs."""

import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, Any
from pathlib import Path

class DependencyVisualizer:
    """Visualizes dependency graphs with different layouts and styles."""
    
    def __init__(self, output_dir: Path):
        """Initialize the visualizer with output directory."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def visualize_graph(self, 
                       graph: nx.DiGraph, 
                       title: str,
                       layout: str = 'spring',
                       node_color: str = 'lightblue',
                       edge_color: str = 'gray',
                       node_size: int = 500,
                       font_size: int = 8) -> Path:
        """Visualize a dependency graph with specified parameters."""
        plt.figure(figsize=(12, 8))
        
        # Choose layout
        if layout == 'spring':
            pos = nx.spring_layout(graph)
        elif layout == 'circular':
            pos = nx.circular_layout(graph)
        elif layout == 'random':
            pos = nx.random_layout(graph)
        else:
            pos = nx.spring_layout(graph)
            
        # Draw nodes
        nx.draw_networkx_nodes(graph, pos,
                             node_color=node_color,
                             node_size=node_size)
                             
        # Draw edges
        nx.draw_networkx_edges(graph, pos,
                             edge_color=edge_color,
                             arrows=True)
                             
        # Draw labels
        nx.draw_networkx_labels(graph, pos,
                              font_size=font_size)
                              
        plt.title(title)
        plt.axis('off')
        
        # Save the plot
        output_path = self.output_dir / f"{title.lower().replace(' ', '_')}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
        
    def visualize_dependency_types(self,
                                 graph: nx.DiGraph,
                                 title: str) -> Path:
        """Visualize graph with different colors for different dependency types."""
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(graph)
        
        # Get unique edge types
        edge_types = {data['type'] for _, _, data in graph.edges(data=True)}
        colors = plt.cm.tab10(range(len(edge_types)))
        color_map = dict(zip(edge_types, colors))
        
        # Draw nodes
        nx.draw_networkx_nodes(graph, pos,
                             node_color='lightblue',
                             node_size=500)
                             
        # Draw edges by type
        for edge_type in edge_types:
            edges = [(u, v) for u, v, d in graph.edges(data=True)
                    if d['type'] == edge_type]
            nx.draw_networkx_edges(graph, pos,
                                 edgelist=edges,
                                 edge_color=color_map[edge_type],
                                 label=edge_type,
                                 arrows=True)
                                 
        # Draw labels
        nx.draw_networkx_labels(graph, pos,
                              font_size=8)
                              
        plt.title(title)
        plt.legend()
        plt.axis('off')
        
        # Save the plot
        output_path = self.output_dir / f"{title.lower().replace(' ', '_')}_types.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
        
    def visualize_subgraph(self,
                          graph: nx.DiGraph,
                          nodes: list,
                          title: str) -> Path:
        """Visualize a subgraph containing specified nodes."""
        subgraph = graph.subgraph(nodes)
        return self.visualize_graph(subgraph, title)
        
    def generate_report(self,
                       graphs: Dict[str, nx.DiGraph],
                       output_path: Path) -> None:
        """Generate a report with visualizations of multiple graphs."""
        report = []
        report.append("# Dependency Analysis Report\n")
        
        for name, graph in graphs.items():
            # Add graph statistics
            report.append(f"## {name}\n")
            report.append(f"- Nodes: {len(graph.nodes())}")
            report.append(f"- Edges: {len(graph.edges())}")
            report.append(f"- Components: {nx.number_weakly_connected_components(graph)}\n")
            
            # Add visualization
            viz_path = self.visualize_graph(graph, name)
            report.append(f"![{name}]({viz_path.relative_to(self.output_dir)})\n")
            
            # Add dependency type visualization
            type_viz_path = self.visualize_dependency_types(graph, f"{name} Types")
            report.append(f"![{name} Types]({type_viz_path.relative_to(self.output_dir)})\n")
            
        # Write report
        output_path.write_text('\n'.join(report)) 