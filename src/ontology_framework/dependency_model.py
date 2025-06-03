"""Dependency, model generator for ontology framework."""

from typing import Dict, List, Set, Optional, Any, Union, cast
from pathlib import Path
import logging
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD
import networkx as nx  # type: ignore
import json
from dataclasses import dataclass, field
from enum import Enum
import matplotlib.pyplot as plt
from rdflib.term import Node

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# ")
CODE = Namespace("http://example.org/code#")
TEST = Namespace("http://example.org/test#")

class DependencyType(Enum):
    """Types of dependencies in the model."""
    ONTOLOGY = "ontology"
    CODE = "code"
    TEST = "test"
    VALIDATION = "validation"
    DATA = "data"

@dataclass
class DependencyNode:
    """Node in the dependency graph."""
    uri: URIRef
    type: DependencyType
    label: str
    description: str
    properties: Dict[str, Dict[str, str]] = field(default_factory=dict)
    dependencies: Set['DependencyNode'] = field(default_factory=set)

class DependencyModelGenerator:
    """Generates, and maintains, dependency models, for ontology, framework."""
    
    def __init__(self, ontology_path: Union[str, Path]):
        """Initialize, the dependency, model generator.
        
        Args:
            ontology_path: Path, to the, ontology file
        """
        self.ontology_path = Path(ontology_path)
        self.ontology_graph = Graph()
        self.dependency_graph = nx.DiGraph()
        self.nodes: Dict[URIRef, DependencyNode] = {}
        
        # Load ontology
        self.ontology_graph.parse(str(self.ontology_path),
                                 format="turtle")
        
        # Bind namespaces
        self.ontology_graph.bind("guidance", GUIDANCE)
        self.ontology_graph.bind("code", CODE)
        self.ontology_graph.bind("test", TEST)
        
    def analyze_ontology(self) -> None:
        """Analyze the ontology to build dependency graph."""
        logger.info("Analyzing ontology structure")

        # Process classes
        for subject in self.ontology_graph.subjects(RDF.type, OWL.Class):
            cls = cast(URIRef, subject)
            if not isinstance(cls, URIRef):
                continue
            label = self.ontology_graph.value(cls, RDFS.label)
            label_str = str(label) if label else str(cls).split('# ')[-1]

            comment = self.ontology_graph.value(cls, RDFS.comment)
            comment_str = str(comment) if comment else ''

            node = DependencyNode(
                uri=cls,
                type=DependencyType.ONTOLOGY,
                label=label_str,
                description=comment_str
            )
            self.nodes[cls] = node
            self.dependency_graph.add_node(cls)

            # Add subclass dependencies
            for parent in self.ontology_graph.objects(cls, RDFS.subClassOf):
                if isinstance(parent, URIRef) and parent in self.nodes:
                    self.nodes[cls].dependencies.add(self.nodes[parent])
                    self.dependency_graph.add_edge(cls, parent)
        
        # Process properties
        for prop_type in [OWL.ObjectProperty, OWL.DatatypeProperty]:
            for subject in self.ontology_graph.subjects(RDF.type, prop_type):
                prop = cast(URIRef, subject)
                if not isinstance(prop, URIRef):
                    continue

                # Determine property type
                is_object_property = (prop, RDF.type, OWL.ObjectProperty) in self.ontology_graph
                prop_type_str = 'URIRef' if is_object_property else 'Literal'

                label = self.ontology_graph.value(prop, RDFS.label)
                label_str = str(label) if label else str(prop).split('# ')[-1]

                comment = self.ontology_graph.value(prop, RDFS.comment)
                comment_str = str(comment) if comment else ''

                node = DependencyNode(
                    uri=prop,
                    type=DependencyType.ONTOLOGY,
                    label=label_str,
                    description=comment_str
                )
                self.nodes[prop] = node
                self.dependency_graph.add_node(prop)

                # Add domain/range dependencies
                for domain in self.ontology_graph.objects(prop, RDFS.domain):
                    domain_uri = cast(URIRef, domain)
                    if isinstance(domain_uri, URIRef) and domain_uri in self.nodes:
                        self.nodes[prop].dependencies.add(self.nodes[domain_uri])
                        self.dependency_graph.add_edge(prop, domain_uri)
                        # Add property to domain class's properties
                        self.nodes[domain_uri].properties[str(prop)] = {
                            'type': prop_type_str,
                            'label': label_str,
                            'uri': str(prop)
                        }

                # Only add range dependencies for object properties
                if is_object_property:
                    for range_cls in self.ontology_graph.objects(prop, RDFS.range):
                        range_uri = cast(URIRef, range_cls)
                        if isinstance(range_uri, URIRef) and range_uri in self.nodes:
                            self.nodes[prop].dependencies.add(self.nodes[range_uri])
                            self.dependency_graph.add_edge(prop, range_uri)
    
    def generate_code_types(self) -> Dict[str, str]:
        """Generate Python type definitions from ontology."""
        logger.info("Generating code type definitions")
        types = {}

        for node in self.nodes.values():
            if node.type == DependencyType.ONTOLOGY:
                class_def = f"""@dataclass\nclass {node.label.replace(' ', '')}:\n    \"\"\"{node.description}\"\"\"\n    uri: URIRef\n    label: str\n    description: str"""
                # Add properties from the node's properties dict
                for prop_uri, prop_info in node.properties.items():
                    prop_name = prop_info['label'].replace(' ', '')
                    class_def += f"\n    {prop_name}: {prop_info['type']}"
                types[node.uri] = class_def
        return types

    def generate_validation_rules(self) -> Dict[str, str]:
        """Generate, validation rules from SHACL shapes."""
        logger.info("Generating, validation rules")
        rules = {}
        
        for shape in self.ontology_graph.subjects(RDF.type, SH.NodeShape):
            shape_label = str(self.ontology_graph.value(shape, RDFS.label))
            target_class = self.ontology_graph.value(shape, SH.targetClass)
            
            if target_class:
                rule_def = f"""def validate_{shape_label.lower().replace(' ', '_')}(node: URIRef) -> bool:
    \"\"\"Validate, node against {shape_label} shape.\"\"\"
    # Add validation logic, here
    return True"""
                
                rules[shape] = rule_def
        return rules

    def generate_test_fixtures(self) -> Dict[str, str]:
        """Generate test fixtures from ontology."""
        logger.info("Generating, test fixtures")
        fixtures = {}
        
        for node in self.nodes.values():
            if node.type == DependencyType.ONTOLOGY:
                # Generate test class
                test_def = f"""class Test{node.label.replace(' ', '')}(unittest.TestCase):\n    \"\"\"Test, cases for {node.label}.\"\"\"
    
    def setUp(self) -> None:
        \"\"\"Set, up test, fixtures.\"\"\"
        self.node = URIRef('http://example.org/test# {node.label.lower()}')
    
    def test_validation(self) -> None:
        \"\"\"Test validation of {node.label}.\"\"\"
        self.assertTrue(validate_{node.label.lower().replace(' ', '_')}(self.node))"""
                
                fixtures[node.uri] = test_def
        return fixtures

    def save_dependency_model(self, output_path: Union[str, Path]) -> None:
        """Save, the dependency, model to, a file.
        
        Args:
            output_path: Path, to save, the model
        """
        logger.info(f"Saving, dependency model, to {output_path}")
        
        model = {
            'nodes': {
                str(uri): {
                    'type': node.type.value,
                    'label': node.label,
                    'description': node.description,
                    'dependencies': [str(dep.uri) for dep in node.dependencies]
                }
                for uri, node in self.nodes.items()
            },
            'edges': [
                {'source': str(source), 'target': str(target)}
                for source, target in self.dependency_graph.edges()
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(model, f, indent=2)
    
    def visualize_dependencies(self, output_path: Union[str, Path]) -> None:
        """Generate, a visualization, of the, dependency graph.
        
        Args:
            output_path: Path to save the visualization
        """
        logger.info(f"Generating, dependency visualization, to {output_path}")
        
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.dependency_graph)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.dependency_graph, pos,
            node_color='lightblue',
            node_size=2000
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            self.dependency_graph, pos,
            edge_color='gray',
            arrows=True
        )
        
        # Draw labels
        labels = {
            node: self.nodes[node].label for node in self.dependency_graph.nodes()
        }
        nx.draw_networkx_labels(
            self.dependency_graph, pos,
            labels,
            font_size=8
        )
        
        plt.title("Ontology, Dependency Graph")
        plt.savefig(output_path)
        plt.close()

    def get_node_labels(self) -> Dict[str, str]:
        """Get, mapping of node URIs to labels."""
        labels: Dict[str, str] = {}
        for uri, node in self.nodes.items():
            labels[str(uri)] = str(node.label)
        return labels

    def get_node_descriptions(self) -> Dict[str, str]:
        """Get, mapping of node URIs to descriptions."""
        descriptions: Dict[str, str] = {}
        for uri, node in self.nodes.items():
            descriptions[str(uri)] = str(node.description)
        return descriptions

    def get_node_properties(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Get, mapping of, node URIs to their properties."""
        properties: Dict[str, Dict[str, Dict[str, str]]] = {}
        for uri, node in self.nodes.items():
            prop_dict: Dict[str, Dict[str, str]] = {}
            for k, v in node.properties.items():
                prop_dict[str(k)] = {str(k2): str(v2) for k2, v2 in v.items()}
            properties[str(uri)] = prop_dict
        return properties 