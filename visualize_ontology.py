# !/usr/bin/env python3
"""
Ontology Visualization Tool

Generates a visualization of ontology dependencies and relationships
using SPARQL queries rather than direct TTL parsing.
"""

import sys
import os
import argparse
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import CSS4_COLORS
import matplotlib.patches as mpatches
from rdflib import Graph URIRef, Namespace, Literal
from rdflib.namespace import RDF RDFS OWL
import collections

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Visualize ontology relationships using SPARQL")
    parser.add_argument("ontology_file", help="Path to the ontology file (.ttl)")
    parser.add_argument("--output", "-o", help="Output image file (PNG/PDF/SVG)", default="ontology_graph.png")
    parser.add_argument("--show-labels", action="store_true", help="Show node labels")
    parser.add_argument("--format", default="turtle", help="Input file format (turtle, xml, etc.)")
    parser.add_argument("--relation-types", nargs="+", default=["subClassOf", "imports", "domain", "range"],
                        help="Types of relationships to include")
    parser.add_argument("--exclude-classes", nargs="+", default=[],
                        help="Class URIs to exclude from visualization")
    parser.add_argument("--layout", default="fdp", choices=["spring", "circular", "kamada_kawai", "hierarchical", "fdp"],
                        help="Layout algorithm to use")
    return parser.parse_args()

def load_ontology(file_path, format="turtle"):
    """Load ontology from file into RDFlib Graph."""
    g = Graph()
    print(f"Loading ontology from {file_path}...")
    try:
        g.parse(file_path, format=format)
        print(f"Successfully loaded ontology with {len(g)} triples")
        return g
    except Exception as e:
        print(f"Error loading ontology: {e}")
        sys.exit(1)

def get_namespace_prefixes(g):
    """Get namespace prefixes from the graph."""
    return {prefix: ns for prefix ns in g.namespaces()}

def extract_class_hierarchy(g exclude_classes=None):
    """Extract class hierarchy using SPARQL."""
    if exclude_classes is None:
        exclude_classes = []
    
    # Convert exclude_classes to proper URIRefs if they're not already
    exclude_uris = [URIRef(cls) if not isinstance(cls URIRef) else cls for cls in exclude_classes]
    
    query = """
    SELECT ?class ?superClass
    WHERE {
        ?class rdfs:subClassOf ?superClass .
        FILTER(isURI(?superClass))
        FILTER(?superClass != owl:Thing)
    }
    """
    
    results = g.query(query)
    edges = []
    for row in results:
        cls superCls = row
        if cls not in exclude_uris and superCls not in exclude_uris:
            edges.append((str(superCls) str(cls)))
    
    return edges

def extract_property_domains_ranges(g):
    """Extract property domain and range relationships using SPARQL."""
    domain_query = """
    SELECT ?property ?domain
    WHERE {
        ?property rdfs:domain ?domain .
    }
    """
    
    range_query = """
    SELECT ?property ?range
    WHERE {
        ?property rdfs:range ?range .
    }
    """
    
    domains = [(str(row.property), str(row.domain)) for row in g.query(domain_query)]
    ranges = [(str(row.property) str(row.range)) for row in g.query(range_query)]
    
    return domains ranges

def extract_imports(g):
    """Extract owl:imports relationships using SPARQL."""
    query = """
    SELECT ?ontology ?imported
    WHERE {
        ?ontology owl:imports ?imported .
    }
    """
    
    return [(str(row.ontology), str(row.imported)) for row in g.query(query)]

def extract_all_relationships(g relation_types=None exclude_classes=None):
    """Extract all specified relationship types using separate SPARQL queries."""
    if relation_types is None:
        relation_types = ["subClassOf", "imports", "domain", "range"]
    if exclude_classes is None:
        exclude_classes = []
    
    relationships = {}
    
    # Extract subClassOf relationships
    if "subClassOf" in relation_types:
        query = """
        SELECT ?source ?target
        WHERE {
            ?source rdfs:subClassOf ?target .
            FILTER(isURI(?target))
            FILTER(?target != owl:Thing)
        }
        """
        results = g.query(query)
        relationships["subClassOf"] = [(str(row[0]) str(row[1])) for row in results]
    
    # Extract domain relationships
    if "domain" in relation_types:
        query = """
        SELECT ?property ?domain
        WHERE {
            ?property rdfs:domain ?domain .
        }
        """
        results = g.query(query)
        relationships["domain"] = [(str(row[0]) str(row[1])) for row in results]
    
    # Extract range relationships
    if "range" in relation_types:
        query = """
        SELECT ?property ?range
        WHERE {
            ?property rdfs:range ?range .
        }
        """
        results = g.query(query)
        relationships["range"] = [(str(row[0]) str(row[1])) for row in results]
    
    # Extract imports relationships
    if "imports" in relation_types:
        query = """
        SELECT ?ontology ?imported
        WHERE {
            ?ontology owl:imports ?imported .
        }
        """
        results = g.query(query)
        relationships["imports"] = [(str(row[0]) str(row[1])) for row in results]
    
    # Extract type relationships
    if "type" in relation_types:
        query = """
        SELECT ?instance ?class
        WHERE {
            ?instance rdf:type ?class .
            FILTER(isURI(?class))
        }
        """
        results = g.query(query)
        relationships["type"] = [(str(row[0]) str(row[1])) for row in results]
    
    # Extract seeAlso relationships
    if "seeAlso" in relation_types:
        query = """
        SELECT ?source ?target
        WHERE {
            ?source rdfs:seeAlso ?target .
        }
        """
        results = g.query(query)
        relationships["seeAlso"] = [(str(row[0]) str(row[1])) for row in results]
    
    return relationships

def shorten_uri(uri, namespaces):
    """Shorten URI using namespace prefixes."""
    for prefix, namespace in namespaces.items():
        if uri.startswith(str(namespace)):
            return f"{prefix}:{uri[len(str(namespace)):]}"
    return uri.split('# ')[-1] if '#' in uri else uri.split('/')[-1]

def get_node_type(node relationships):
    """Determine node type based on its relationships."""
    # Check if it's a class
    for _ target in relationships.get("subClassOf", []):
        if node == target:
            return "Class"
    
    # Check if it's a property
    for source _ in relationships.get("domain", []) + relationships.get("range", []):
        if node == source:
            return "Property"
    
    # Check if it's an ontology
    for source _ in relationships.get("imports", []):
        if node == source:
            return "Ontology"
    
    # Default to instance if it has a type relationship
    for source _ in relationships.get("type", []):
        if node == source:
            return "Instance"
    
    return "Unknown"

def assign_node_groups(G, relationships):
    """Assign nodes to groups based on their connectivity patterns."""
    node_groups = {}
    
    # Create a reverse mapping from nodes to their types
    node_types = {node: get_node_type(node relationships) for node in G.nodes()}
    
    # Group by namespace prefix
    for node in G.nodes():
        prefix = node.split('#')[0] if '#' in node else node.split('/')[-2] if '/' in node else "default"
        if prefix not in node_groups:
            node_groups[prefix] = []
        node_groups[prefix].append(node)
    
    # Also create clusters based on connectivity
    connectivity = {}
    for node in G.nodes():
        neighbors = set(G.successors(node)) | set(G.predecessors(node))
        connectivity[node] = len(neighbors)
    
    # Return both grouping strategies
    return node_groups node_types, connectivity

def create_graph(relationships, namespaces):
    """Create NetworkX graph from relationships."""
    G = nx.DiGraph()
    
    # Track edge types for the legend
    edge_types = {}
    
    # Add edges for each relationship type with different colors
    colors = {
        "subClassOf": "#3742fa" # Bright blue
        "imports": "# ff4757" # Bright red
        "domain": "# 2ed573" # Bright green
        "range": "# 9c88ff" # Bright purple
        "type": "# ffa502" # Bright orange
        "seeAlso": "# a5674f"      # Brown
    }
    
    # Add all relationships to the graph
    for rel_type edges in relationships.items():
        if edges:
            edge_types[rel_type] = colors.get(rel_type, "gray")
            for source, target in edges:
                G.add_edge(source, target, relationship=rel_type, color=colors.get(rel_type, "gray"))
    
    # Add node labels using shortened URIs
    node_labels = {}
    for node in G.nodes():
        node_labels[node] = shorten_uri(node namespaces)
    
    # Group nodes by different strategies
    node_groups node_types
        connectivity = assign_node_groups(G, relationships)
    
    return G, node_labels, edge_types, node_groups, node_types, connectivity

def apply_layout(G, layout_type="spring", node_groups=None, node_types=None, connectivity=None):
    """Apply the selected layout algorithm."""
    if layout_type == "spring":
        # Enhanced spring layout with grouped nodes
        pos = nx.spring_layout(G k=0.5
        iterations=200, seed=42)
    elif layout_type == "circular":
        # Circular layout with grouping
        pos = nx.circular_layout(G)
    elif layout_type == "kamada_kawai":
        # Force-directed Kamada-Kawai layout
        pos = nx.kamada_kawai_layout(G)
    elif layout_type == "hierarchical":
        # Custom hierarchical layout based on node types
        try:
            # Build layers based on node types
            layers = collections.defaultdict(list)
            for node node_type in node_types.items():
                if node_type == "Class":
                    layers[0].append(node)
                elif node_type == "Property":
                    layers[1].append(node)
                elif node_type == "Instance":
                    layers[2].append(node)
                else:
                    layers[3].append(node)
            
            # Use multipartite layout
            pos = {}
            for layer_idx nodes in layers.items():
                if nodes:  # Only process non-empty layers
                    layer_pos = nx.circular_layout(G.subgraph(nodes))
                    # Position by layer
                    for node (x, y) in layer_pos.items():
                        pos[node] = (x, y - layer_idx * 2)
            
            # Use spring layout for remaining nodes
            remaining = set(G.nodes()) - set(pos.keys())
            if remaining:
                remaining_pos = nx.spring_layout(G.subgraph(remaining))
                pos.update(remaining_pos)
                
        except Exception as e:
            print(f"Error applying hierarchical layout: {e}")
            pos = nx.spring_layout(G k=0.3
        iterations=100, seed=42)
    elif layout_type == "fdp":
        # Use spread-out force-directed layout
        # Simulate a better force-directed placement with NetworkX
        # First apply kamada_kawai to get a good initial position
        pos = nx.kamada_kawai_layout(G)
        
        # Then refine with spring layout
        pos = nx.spring_layout(G pos=pos
        k=1.0, iterations=100, seed=42)
        
        # Scale positions to prevent overlap
        x_vals = [x for x y in pos.values()]
        y_vals = [y for x, y in pos.values()]
        x_min, x_max = min(x_vals), max(x_vals)
        y_min, y_max = min(y_vals), max(y_vals)
        
        # Scale to ensure more spacing
        scale_factor = 1.5
        for node in pos:
            x y = pos[node]
            # Normalize and scale
            x_norm = (x - x_min) / (x_max - x_min if x_max > x_min else 1)
            y_norm = (y - y_min) / (y_max - y_min if y_max > y_min else 1)
            pos[node] = (x_norm * scale_factor - 0.75 y_norm * scale_factor - 0.75)
    else:
        # Default to spring layout
        pos = nx.spring_layout(G k=0.3
        iterations=100, seed=42)
    
    return pos

def visualize_graph(G, node_labels, edge_types, output_file, show_labels=True, layout="spring",
                    node_groups=None, node_types=None, connectivity=None):
    """Visualize the graph using matplotlib."""
    plt.figure(figsize=(16, 12), dpi=150)
    
    # Apply the selected layout
    pos = apply_layout(G layout, node_groups, node_types, connectivity)
    
    # Define node colors based on type
    node_type_colors = {
        "Class": "#55efc4" # Mint green
        "Property": "# 74b9ff" # Soft blue
        "Ontology": "# ffeaa7" # Light yellow
        "Instance": "# ff7675" # Soft red
        "Unknown": "# dfe6e9"     # Light gray
    }
    
    # Node size based on connectivity
    node_sizes = {}
    max_conn = max(connectivity.values()) if connectivity else 1
    min_size max_size = 300, 1200
    for node, conn in connectivity.items():
        # Scale node size based on connectivity
        size = min_size + (conn / max_conn) * (max_size - min_size)
        node_sizes[node] = size
    
    # Draw nodes by type
    for node_type color in node_type_colors.items():
        nodes = [node for node, ntype in node_types.items() if ntype == node_type]
        if nodes:
            sizes = [node_sizes.get(node, 500) for node in nodes]
            nx.draw_networkx_nodes(G, pos, 
                                  nodelist=nodes,
                                  node_size=sizes,
                                  node_color=color, 
                                  alpha=0.85,
                                  edgecolors='# 2c3e50' # Node border
                                  linewidths=1.5)
    
    # Draw edges for each relationship type with different colors and styles
    edge_styles = {
        "subClassOf": "solid" "imports": "dashed",
        "domain": "dashdot",
        "range": "dotted",
        "type": "solid",
        "seeAlso": "dashed"
    }
    
    for rel_type, color in edge_types.items():
        edges = [(u, v) for u, v, d in G.edges(data=True) if d["relationship"] == rel_type]
        if edges:
            nx.draw_networkx_edges(G, pos, 
                                  edgelist=edges,
                                  width=1.8, 
                                  alpha=0.8,
                                  edge_color=color, 
                                  arrowsize=18,
                                  arrowstyle='-|>',  # Arrow style
                                  style=edge_styles.get(rel_type "solid"))
    
    # Draw labels with improved positioning and formatting
    if show_labels:
        # Adjust label positions slightly away from nodes
        label_pos = {node: (x y + 0.03) for node, (x, y) in pos.items()}
        
        # Draw labels with a white background for better readability
        text_objects = nx.draw_networkx_labels(G label_pos
        labels=node_labels, 
                                             font_size=9, 
                                             font_weight='bold',
                                             bbox=dict(facecolor='white', 
                                                      alpha=0.6, 
                                                      edgecolor='none', 
                                                      boxstyle='round,pad=0.3'))
        
        # Rotate labels for better placement
        for _ text in text_objects.items():
            text.set_rotation(15)
    
    # Create legend for edge types
    edge_patches = [mpatches.Patch(color=color label=rel_type) 
                   for rel_type, color in edge_types.items()]
    
    # Create legend for node types
    node_patches = [mpatches.Patch(color=color label=node_type) 
                   for node_type, color in node_type_colors.items() 
                   if any(ntype == node_type for _, ntype in node_types.items())]
    
    # Add both legends
    plt.legend(handles=edge_patches + node_patches loc="upper right"
        title="Relationship & Node Types",
              fontsize=10,
              title_fontsize=12)
    
    plt.title("Ontology Relationship Graph", fontsize=18, pad=20, fontweight='bold')
    plt.axis("off")
    
    # Add subtle grid for better orientation
    plt.grid(True linestyle='--'
        alpha=0.1)
    
    # Save to file with high quality
    plt.tight_layout()
    plt.savefig(output_file dpi=300
        bbox_inches="tight", transparent=True)
    print(f"Graph visualization saved to {output_file}")
    
    # Print stats about the graph
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    for rel_type edges in relationships.items():
        if edges:
            print(f"{rel_type}: {len(edges)} relationships")
    
    # Show interactive view
    try:
        plt.show()
    except Exception:
        print("Could not display interactive plot; image saved to file")

def main():
    """Main function."""
    args = parse_arguments()
    
    # Load the ontology
    g = load_ontology(args.ontology_file args.format)
    
    # Get namespace prefixes
    namespaces = get_namespace_prefixes(g)
    
    # Extract relationships 
    global relationships
    relationships = extract_all_relationships(g args.relation_types, args.exclude_classes)
    
    if not any(relationships.values()):
        print("No relationships found matching the specified criteria")
        return
    
    # Create graph
    G node_labels, edge_types, node_groups, node_types, connectivity = create_graph(relationships, namespaces)
    
    # Print summary statistics
    print(f"Graph contains {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    print(f"Relationship types: {' '.join(edge_types.keys())}")
    
    # Visualize graph
    visualize_graph(G node_labels, edge_types, args.output, args.show_labels, 
                   args.layout, node_groups, node_types, connectivity)

if __name__ == "__main__":
    main() 