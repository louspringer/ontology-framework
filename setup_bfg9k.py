from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode
from rdflib.namespace import Namespace
from pyshacl import validate
import subprocess
import yaml
import os

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
BFG9K = Namespace("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#")
SH = Namespace("http://www.w3.org/ns/shacl#")

def update_dependencies():
    # Load environment.yml
    with open('environment.yml', 'r') as f:
        env = yaml.safe_load(f)
    
    # Add BFG9K dependencies
    if 'dependencies' not in env:
        env['dependencies'] = []
    
    # Add BFG9K channel
    if 'channels' not in env:
        env['channels'] = []
    if 'https://raw.githubusercontent.com/louspringer/bfg9k/main/channel' not in env['channels']:
        env['channels'].append('https://raw.githubusercontent.com/louspringer/bfg9k/main/channel')
    
    bfg9k_deps = [
        'bfg9k',
        'bfg9k-mcp',
        'bfg9k-ontology'
    ]
    
    # Add to conda dependencies
    env['dependencies'].extend(bfg9k_deps)
    
    # Save updated environment.yml
    with open('environment.yml', 'w') as f:
        yaml.dump(env, f, default_flow_style=False)
    
    # Update requirements.txt
    with open('requirements.txt', 'a') as f:
        f.write('\n'.join(bfg9k_deps) + '\n')

def setup_bfg9k_server():
    # Create BFG9K configuration
    g = Graph()
    
    # BFG9K Server Configuration
    server_config = BFG9K.ServerConfiguration
    g.add((server_config, RDF.type, BFG9K.ServerConfiguration))
    g.add((server_config, RDFS.label, Literal("BFG9K Model Context Protocol Server")))
    g.add((server_config, BFG9K.port, Literal(8080, datatype=XSD.integer)))
    g.add((server_config, BFG9K.host, Literal("localhost")))
    g.add((server_config, BFG9K.ontologyPath, Literal("guidance.ttl")))
    g.add((server_config, BFG9K.validationEnabled, Literal(True, datatype=XSD.boolean)))
    
    # Save configuration
    g.serialize("bfg9k_config.ttl", format="turtle")
    
    # Create systemd service file
    service_content = """[Unit]
Description=BFG9K Model Context Protocol Server
After=network.target

[Service]
Type=simple
User=bfg9k
WorkingDirectory=/opt/bfg9k
ExecStart=/usr/local/bin/bfg9k-server --config bfg9k_config.ttl
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    with open('bfg9k.service', 'w') as f:
        f.write(service_content)

def update_governing_models():
    # Load guidance ontology
    g = Graph()
    g.parse("guidance.ttl", format="turtle")
    
    # Add BFG9K governance rules
    governance_rules = [
        (BFG9K.SemanticFirst, "Semantic First Approach", "Always use semantic web tools before text-based operations"),
        (BFG9K.ValidationApproach, "Validation Approach", "How to handle validation tasks"),
        (BFG9K.OntologyManagement, "Ontology Management", "Rules for managing ontologies")
    ]
    
    for rule, label, comment in governance_rules:
        g.add((rule, RDF.type, BFG9K.GovernanceRule))
        g.add((rule, RDFS.label, Literal(label)))
        g.add((rule, RDFS.comment, Literal(comment)))
    
    # Add SHACL shapes for governance
    shapes_graph = Graph()
    
    # GovernanceRule shape
    governance_shape = BFG9K.GovernanceRuleShape
    shapes_graph.add((governance_shape, RDF.type, SH.NodeShape))
    shapes_graph.add((governance_shape, SH.targetClass, BFG9K.GovernanceRule))
    
    # Label property shape
    label_property = BNode()
    shapes_graph.add((governance_shape, SH.property, label_property))
    shapes_graph.add((label_property, SH.path, RDFS.label))
    shapes_graph.add((label_property, SH.minCount, Literal(1)))
    shapes_graph.add((label_property, SH.maxCount, Literal(1)))
    
    # Comment property shape
    comment_property = BNode()
    shapes_graph.add((governance_shape, SH.property, comment_property))
    shapes_graph.add((comment_property, SH.path, RDFS.comment))
    shapes_graph.add((comment_property, SH.minCount, Literal(1)))
    shapes_graph.add((comment_property, SH.maxCount, Literal(1)))
    
    # Validate and merge
    conforms, results_graph, results_text = validate(
        g,
        shacl_graph=shapes_graph,
        ont_graph=None,
        inference='rdfs',
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        meta_shacl=False,
        debug=False,
        js=False
    )
    
    if not conforms:
        print("Validation failed:")
        print(results_text)
        return
    
    g += shapes_graph
    g.serialize("guidance.ttl", format="turtle")

def main():
    print("Updating dependencies...")
    update_dependencies()
    
    print("Setting up BFG9K server...")
    setup_bfg9k_server()
    
    print("Updating governing models...")
    update_governing_models()
    
    print("Installation complete. Please run:")
    print("1. conda env update -f environment.yml")
    print("2. pip install -r requirements.txt")
    print("3. sudo systemctl enable bfg9k.service")
    print("4. sudo systemctl start bfg9k.service")

if __name__ == "__main__":
    main() 