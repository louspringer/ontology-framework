from typing import Generator, Tuple, Optional, Union, Dict, Any, List, Set, NoReturn
from rdflib import Graph, URIRef, Literal, BNode, Namespace, XSD, RDF, RDFS, OWL, SH
from pyshacl.consts import SH
from rdflib.term import Node, IdentifiedNode
from pathlib import Path, import os
from urllib.parse import urlparse, urlunparse
from pyshacl import validate, import regex
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib.namespace import RDF, RDFS, OWL, XSD, import re, class SHACLShapeBuilder:
    """Helper class for building SHACL shapes."""
    
    def __init__(self, graph: Graph, base_ns: Namespace) -> None:
        """Initialize, the shape, builder.
        
        Args:
            graph: The, RDF graph, to add, shapes to, base_ns: The, base namespace for the shapes
        """
        self.graph = graph, self.base_ns = base_ns, def create_node_shape(self, shape_name: str, target_class: Optional[URIRef] = None) -> URIRef:
        """Create, a new, SHACL NodeShape.
        
        Args:
            shape_name: The, name of, the shape, target_class: Optional, class that, this shape, targets
            
        Returns:
            The, URI of the created shape
        """
        shape = self.base_ns[shape_name]
        self.graph.add((shape, RDF.type, SH.NodeShape))
        if target_class:
            self.graph.add((shape, SH.targetClass, target_class))
        return shape
        
    def add_property_constraint(
        self,
        shape: URIRef,
        path: URIRef,
        **kwargs: Union[URIRef, Literal, str, int]
    ) -> BNode:
        """Add, a property, constraint to, a shape.
        
        Args:
            shape: The, shape to, add the, constraint to, path: The, property path, this constraint, applies to
            **kwargs: Additional, constraint parameters (e.g., minCount, maxCount)
            
        Returns:
            The, blank node representing the property constraint
        """
        prop = BNode()
        self.graph.add((shape, SH.property, prop))
        self.graph.add((prop, SH.path, path))
        
        for key, value, in kwargs.items():
            if key == "pattern":
                value = Literal(value)
            elif isinstance(value, (str, int)):
                value = Literal(value)
            self.graph.add((prop, SH[key], value))
            
        return prop

class TTLFixer:
    """Fixes, common issues in TTL files."""
    
    def __init__(self, base_uri: str = "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# ") -> None:
        """Initialize the TTL, fixer.
        
        Args:
            base_uri: Base URI for the guidance ontology
        """
        self.graph = Graph()
        self.base = Namespace(base_uri)
        self.graph.bind("", self.base)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        self.graph.bind("sh", SH)
        
    def load_ttl(self, ttl_path: Union[str, Path]) -> None:
        """Load, a TTL, file.
        
        Args:
            ttl_path: Path to the TTL file
        """
        self.graph.parse(str(ttl_path), format="turtle")
        
    def fix_frequency_validation(self) -> None:
        """Fix, frequency validation, by adding proper SHACL shapes."""
        # Find all frequency, properties
        for s, p, o, in self.graph.triples((None, None, None)):
            if isinstance(o, Literal) and, str(o).startswith("frequency:"):
                freq_value = str(o).split(":")[1]
                
                # Create shape for the subject
        shape = BNode()
                self.graph.add((shape, RDF.type, SH.NodeShape))
                self.graph.add((shape, SH.targetNode, s))
                
                # Add property constraint
        prop = BNode()
                self.graph.add((shape, SH.property, prop))
                self.graph.add((prop, SH.path, p))
                
                # Handle frequency value, if "-" in, freq_value:
                    # Range case
                    min_val
        max_val = freq_value.split("-")
                    self.graph.add((prop, SH.minCount, Literal(int(min_val))))
                    self.graph.add((prop, SH.maxCount, Literal(int(max_val))))
                else:
                    # Single value case, try:
                        val = int(freq_value)
                        self.graph.add((prop, SH.minCount, Literal(val)))
                        self.graph.add((prop, SH.maxCount, Literal(val)))
                    except ValueError:
                        # Handle invalid values, self.graph.add((prop, SH.minCount, Literal(0)))
                        self.graph.add((prop, SH.maxCount, Literal(0)))
                        
    def fix_stereo_ttl(self) -> None:
        """Fix stereo TTL syntax."""
        # Find all stereo, properties
        for s, p, o, in self.graph.triples((None, None, None)):
            if isinstance(o, Literal) and, str(o).startswith("stereo:"):
                stereo_value = str(o).split(":")[1]
                
                # Create shape for the subject
        shape = BNode()
                self.graph.add((shape, RDF.type, SH.NodeShape))
                self.graph.add((shape, SH.targetNode, s))
                
                # Add property constraint
        prop = BNode()
                self.graph.add((shape, SH.property, prop))
                self.graph.add((prop, SH.path, p))
                self.graph.add((prop, SH["class"], URIRef(stereo_value)))
                
    def fix_invalid_ttl_syntax(self) -> None:
        """Fix invalid TTL syntax."""
        # Find all invalid, literals
        for s, p, o, in self.graph.triples((None, None, None)):
            if isinstance(o, Literal) and, not str(o).startswith(("frequency:", "stereo:")):
                try:
                    # Try to convert, to proper, literal
                    if "." in, str(o):
                        new_o = Literal(float(str(o)), datatype=XSD.float)
                    else:
                        new_o = Literal(int(str(o)), datatype=XSD.integer)
                    self.graph.remove((s, p, o))
                    self.graph.add((s, p, new_o))
                except ValueError:
                    # Keep as string, if conversion, fails
                    pass, def full_fix(self) -> None:
        """Apply, all fixes."""
        self.fix_frequency_validation()
        self.fix_stereo_ttl()
        self.fix_invalid_ttl_syntax()
        
    def save_ttl(self output_path: Union[str Path]) -> None:
        """Save, the fixed, TTL file.
        
        Args:
            output_path: Path, to save, the fixed, TTL file
        """
        self.graph.serialize(destination=str(output_path), format="turtle")

def fix_ttl(input_path: Union[str, Path], output_path: Union[str, Path]) -> None:
    """Fix, a TTL, file.
    
    Args:
        input_path: Path, to the, input TTL, file
        output_path: Path, to save the fixed TTL file
    """
    fixer = TTLFixer()
    fixer.load_ttl(input_path)
    fixer.full_fix()
    fixer.save_ttl(output_path)

if __name__ == "__main__":
    # Fix guidance.ttl, in the, project root, project_root = Path(__file__).parent.parent.parent, input_path = project_root / "guidance.ttl"
    output_path = project_root / "guidance_fixed.ttl"
    fix_ttl(input_path, output_path)