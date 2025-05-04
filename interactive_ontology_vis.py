#!/usr/bin/env python3
"""
Interactive Ontology Visualization Tool

Generates an interactive HTML-based visualization of ontology relationships
with adjustable physics parameters using PyVis and NetworkX.
"""

import sys
import os
import argparse
from pathlib import Path
import networkx as nx
from pyvis.network import Network
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS, OWL
import json

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Create interactive ontology visualization with adjustable physics")
    parser.add_argument("ontology_file", help="Path to the ontology file (.ttl)")
    parser.add_argument("--output", "-o", help="Output HTML file", default="interactive_ontology.html")
    parser.add_argument("--format", default="turtle", help="Input file format (turtle, xml, etc.)")
    parser.add_argument("--relation-types", nargs="+", default=["subClassOf", "imports", "domain", "range", "type", "seeAlso"],
                        help="Types of relationships to include")
    parser.add_argument("--height", default="800px", help="Height of the visualization")
    parser.add_argument("--width", default="100%", help="Width of the visualization")
    parser.add_argument("--physics-enabled", action="store_true", default=True, help="Enable physics simulation")
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
    return {prefix: ns for prefix, ns in g.namespaces()}

def shorten_uri(uri, namespaces):
    """Shorten URI using namespace prefixes."""
    for prefix, namespace in namespaces.items():
        if uri.startswith(str(namespace)):
            return f"{prefix}:{uri[len(str(namespace)):]}"
    return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]

def extract_all_relationships(g, relation_types=None):
    """Extract all specified relationship types using separate SPARQL queries."""
    if relation_types is None:
        relation_types = ["subClassOf", "imports", "domain", "range", "type", "seeAlso"]
    
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
        relationships["subClassOf"] = [(str(row[0]), str(row[1])) for row in results]
    
    # Extract domain relationships
    if "domain" in relation_types:
        query = """
        SELECT ?property ?domain
        WHERE {
            ?property rdfs:domain ?domain .
        }
        """
        results = g.query(query)
        relationships["domain"] = [(str(row[0]), str(row[1])) for row in results]
    
    # Extract range relationships
    if "range" in relation_types:
        query = """
        SELECT ?property ?range
        WHERE {
            ?property rdfs:range ?range .
        }
        """
        results = g.query(query)
        relationships["range"] = [(str(row[0]), str(row[1])) for row in results]
    
    # Extract imports relationships
    if "imports" in relation_types:
        query = """
        SELECT ?ontology ?imported
        WHERE {
            ?ontology owl:imports ?imported .
        }
        """
        results = g.query(query)
        relationships["imports"] = [(str(row[0]), str(row[1])) for row in results]
    
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
        relationships["type"] = [(str(row[0]), str(row[1])) for row in results]
    
    # Extract seeAlso relationships
    if "seeAlso" in relation_types:
        query = """
        SELECT ?source ?target
        WHERE {
            ?source rdfs:seeAlso ?target .
        }
        """
        results = g.query(query)
        relationships["seeAlso"] = [(str(row[0]), str(row[1])) for row in results]
    
    return relationships

def get_node_type(node, relationships):
    """Determine node type based on its relationships."""
    # Check if it's a class
    for _, target in relationships.get("subClassOf", []):
        if node == target:
            return "Class"
    
    # Check if it's a property
    for source, _ in relationships.get("domain", []) + relationships.get("range", []):
        if node == source:
            return "Property"
    
    # Check if it's an ontology
    for source, _ in relationships.get("imports", []):
        if node == source:
            return "Ontology"
    
    # Default to instance if it has a type relationship
    for source, _ in relationships.get("type", []):
        if node == source:
            return "Instance"
    
    return "Unknown"

def create_interactive_graph(relationships, namespaces, height="800px", width="100%", physics_enabled=True):
    """Create an interactive network visualization."""
    # Create a networkx graph from relationships
    G = nx.DiGraph()
    
    # Define node colors based on type
    node_colors = {
        "Class": "#55efc4",      # Mint green
        "Property": "#74b9ff",   # Soft blue
        "Ontology": "#ffeaa7",   # Light yellow
        "Instance": "#ff7675",   # Soft red
        "Unknown": "#dfe6e9"     # Light gray
    }
    
    # Define edge colors
    edge_colors = {
        "subClassOf": "#3742fa",  # Bright blue
        "imports": "#ff4757",     # Bright red
        "domain": "#2ed573",      # Bright green
        "range": "#9c88ff",       # Bright purple
        "type": "#ffa502",        # Bright orange
        "seeAlso": "#a5674f"      # Brown
    }
    
    # Add edges to the graph with relationship types
    for rel_type, edges in relationships.items():
        for source, target in edges:
            G.add_edge(source, target, title=rel_type)
    
    # Get node types
    node_types = {node: get_node_type(node, relationships) for node in G.nodes()}
    
    # Calculate node connectivity for sizing
    connectivity = {}
    for node in G.nodes():
        neighbors = set(G.successors(node)) | set(G.predecessors(node))
        connectivity[node] = len(neighbors)
    
    # Get max connectivity for scaling
    max_conn = max(connectivity.values()) if connectivity else 1
    
    # Create PyVis network
    net = Network(height=height, width=width, directed=True, notebook=False)
    
    # Set physics options for interactive adjustment
    physics_options = {
        "enabled": physics_enabled,
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
            "gravitationalConstant": -50,
            "centralGravity": 0.01,
            "springLength": 100,
            "springConstant": 0.08,
            "damping": 0.4,
            "avoidOverlap": 0.5
        },
        "minVelocity": 0.75,
        "maxVelocity": 50,
        "stabilization": {
            "enabled": True,
            "iterations": 1000,
            "updateInterval": 100,
            "onlyDynamicEdges": False,
            "fit": True
        }
    }
    
    # Add nodes with properties
    for node in G.nodes():
        node_type = node_types.get(node, "Unknown")
        color = node_colors.get(node_type, "#dfe6e9")
        
        # Scale node size based on connectivity (min 10, max 50)
        size = 10 + (connectivity.get(node, 1) / max_conn) * 40
        
        # Create readable label
        label = shorten_uri(node, namespaces)
        
        # Create tooltip with more information
        title = f"{node_type}: {label}<br>{node}"
        
        # Add the node
        net.add_node(node, label=label, title=title, color=color, size=size)
    
    # Add edges with properties
    for source, target, data in G.edges(data=True):
        rel_type = data.get('title', 'Unknown')
        color = edge_colors.get(rel_type, "#7f8c8d")
        
        # Add the edge
        net.add_edge(source, target, title=rel_type, color=color, arrows={'to': {'enabled': True}})
    
    # Configure visualization options
    net.set_options("""
    const options = {
        "nodes": {
            "font": {
                "size": 12,
                "face": "Tahoma",
                "strokeWidth": 3,
                "strokeColor": "#ffffff"
            },
            "borderWidth": 2,
            "shadow": {
                "enabled": true
            }
        },
        "edges": {
            "color": {
                "inherit": false
            },
            "smooth": {
                "type": "dynamic",
                "forceDirection": "none",
                "roundness": 0.5
            },
            "font": {
                "size": 11,
                "face": "Arial",
                "strokeWidth": 2,
                "strokeColor": "#ffffff"
            },
            "width": 2
        },
        "interaction": {
            "navigationButtons": true,
            "keyboard": true,
            "hover": true,
            "multiselect": true,
            "tooltipDelay": 100
        },
        "physics": %s
    }
    """ % json.dumps(physics_options))
    
    # Add a legend
    legend_html = """
    <div style="position: absolute; top: 10px; right: 10px; padding: 10px; 
                background-color: rgba(255, 255, 255, 0.8); border-radius: 5px; 
                border: 1px solid #ccc; z-index: 1000;">
        <h3 style="margin-top: 0;">Legend</h3>
        <h4>Node Types</h4>
        <ul style="padding-left: 20px; margin-bottom: 10px;">
    """
    
    for node_type, color in node_colors.items():
        legend_html += f'<li><span style="display:inline-block; width:12px; height:12px; background:{color}; margin-right:5px;"></span>{node_type}</li>'
    
    legend_html += """
        </ul>
        <h4>Relationship Types</h4>
        <ul style="padding-left: 20px; margin-bottom: 5px;">
    """
    
    for rel_type, color in edge_colors.items():
        if rel_type in relationships and relationships[rel_type]:
            legend_html += f'<li><span style="display:inline-block; width:12px; height:12px; background:{color}; margin-right:5px;"></span>{rel_type}</li>'
    
    legend_html += """
        </ul>
    </div>
    """
    
    # Add controls for adjusting physics parameters
    physics_controls = """
    <div style="position: absolute; top: 10px; left: 10px; padding: 10px; 
                background-color: rgba(255, 255, 255, 0.8); border-radius: 5px; 
                border: 1px solid #ccc; z-index: 1000; max-width: 300px;">
        <h3 style="margin-top: 0;">Physics Controls</h3>
        
        <div style="margin-bottom: 10px;">
            <label for="physicsEnabled">Physics Enabled:</label>
            <input type="checkbox" id="physicsEnabled" checked onchange="togglePhysics(this.checked)">
        </div>
        
        <div style="margin-bottom: 10px;">
            <label for="gravitationalConstant">Gravitational Constant:</label>
            <input type="range" id="gravitationalConstant" min="-200" max="0" value="-50" 
                  onchange="updatePhysics('forceAtlas2Based.gravitationalConstant', this.value)">
            <span id="gravitationalConstantValue">-50</span>
        </div>
        
        <div style="margin-bottom: 10px;">
            <label for="centralGravity">Central Gravity:</label>
            <input type="range" id="centralGravity" min="0" max="1" step="0.01" value="0.01" 
                  onchange="updatePhysics('forceAtlas2Based.centralGravity', this.value)">
            <span id="centralGravityValue">0.01</span>
        </div>
        
        <div style="margin-bottom: 10px;">
            <label for="springLength">Spring Length:</label>
            <input type="range" id="springLength" min="10" max="500" value="100" 
                  onchange="updatePhysics('forceAtlas2Based.springLength', this.value)">
            <span id="springLengthValue">100</span>
        </div>
        
        <div style="margin-bottom: 10px;">
            <label for="springConstant">Spring Constant:</label>
            <input type="range" id="springConstant" min="0" max="1" step="0.01" value="0.08" 
                  onchange="updatePhysics('forceAtlas2Based.springConstant', this.value)">
            <span id="springConstantValue">0.08</span>
        </div>
        
        <div style="margin-bottom: 10px;">
            <label for="damping">Damping:</label>
            <input type="range" id="damping" min="0" max="1" step="0.01" value="0.4" 
                  onchange="updatePhysics('forceAtlas2Based.damping', this.value)">
            <span id="dampingValue">0.4</span>
        </div>
        
        <div style="margin-bottom: 10px;">
            <label for="avoidOverlap">Avoid Overlap:</label>
            <input type="range" id="avoidOverlap" min="0" max="1" step="0.01" value="0.5" 
                  onchange="updatePhysics('forceAtlas2Based.avoidOverlap', this.value)">
            <span id="avoidOverlapValue">0.5</span>
        </div>
        
        <div>
            <button onclick="resetPhysics()">Reset Physics</button>
            <button onclick="stabilize()">Stabilize</button>
        </div>
    </div>
    
    <script>
        // Wait for the network to be created
        setTimeout(function() {
            // Function to update physics parameters
            window.updatePhysics = function(param, value) {
                // Update the displayed value
                document.getElementById(param.split('.')[1] + 'Value').textContent = value;
                
                // Get current physics options
                const physics = network.physics.options;
                
                // Update the specific parameter
                const [category, property] = param.split('.');
                physics[category][property] = parseFloat(value);
                
                // Apply the updated physics options
                network.setOptions({ physics: physics });
            };
            
            // Function to toggle physics
            window.togglePhysics = function(enabled) {
                network.setOptions({ physics: { enabled: enabled } });
            };
            
            // Function to reset physics to default values
            window.resetPhysics = function() {
                const defaultPhysics = {
                    enabled: true,
                    solver: "forceAtlas2Based",
                    forceAtlas2Based: {
                        gravitationalConstant: -50,
                        centralGravity: 0.01,
                        springLength: 100,
                        springConstant: 0.08,
                        damping: 0.4,
                        avoidOverlap: 0.5
                    },
                    stabilization: {
                        enabled: true,
                        iterations: 1000,
                        updateInterval: 100,
                        onlyDynamicEdges: false,
                        fit: true
                    }
                };
                
                // Reset the sliders to default values
                document.getElementById('gravitationalConstant').value = -50;
                document.getElementById('gravitationalConstantValue').textContent = -50;
                document.getElementById('centralGravity').value = 0.01;
                document.getElementById('centralGravityValue').textContent = 0.01;
                document.getElementById('springLength').value = 100;
                document.getElementById('springLengthValue').textContent = 100;
                document.getElementById('springConstant').value = 0.08;
                document.getElementById('springConstantValue').textContent = 0.08;
                document.getElementById('damping').value = 0.4;
                document.getElementById('dampingValue').textContent = 0.4;
                document.getElementById('avoidOverlap').value = 0.5;
                document.getElementById('avoidOverlapValue').textContent = 0.5;
                document.getElementById('physicsEnabled').checked = true;
                
                // Apply default physics
                network.setOptions({ physics: defaultPhysics });
            };
            
            // Function to stabilize the network
            window.stabilize = function() {
                network.stabilize();
            };
        }, 1000); // Wait 1 second for the network to initialize
    </script>
    """
    
    # Return the configured network and HTML additions
    return net, legend_html + physics_controls

def save_interactive_graph(net, html_additions, output_file):
    """Save the interactive graph to an HTML file with custom additions."""
    # Generate the HTML
    net.save_graph(output_file)
    
    # Add the custom HTML to the generated file
    with open(output_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Insert our custom HTML before the closing body tag
    modified_html = html_content.replace('</body>', f'{html_additions}</body>')
    
    # Write the modified HTML back to the file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_html)
    
    print(f"Interactive graph saved to {output_file}")
    print(f"Open this file in a web browser to view and interact with the visualization")

def main():
    """Main function."""
    args = parse_arguments()
    
    # Load the ontology
    g = load_ontology(args.ontology_file, args.format)
    
    # Get namespace prefixes
    namespaces = get_namespace_prefixes(g)
    
    # Extract relationships
    relationships = extract_all_relationships(g, args.relation_types)
    
    if not any(relationships.values()):
        print("No relationships found matching the specified criteria")
        return
    
    # Print relationship statistics
    print("Extracted relationships:")
    for rel_type, edges in relationships.items():
        if edges:
            print(f"  {rel_type}: {len(edges)} relationships")
    
    # Create interactive network
    net, html_additions = create_interactive_graph(relationships, namespaces, 
                                                 height=args.height, 
                                                 width=args.width,
                                                 physics_enabled=args.physics_enabled)
    
    # Save the interactive graph
    save_interactive_graph(net, html_additions, args.output)

if __name__ == "__main__":
    main() 