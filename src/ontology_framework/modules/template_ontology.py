"""Module for template ontology functionality."""

from typing import List, Dict, Any, Optional, Union, Tuple
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
from pathlib import Path
from .ontology import Ontology
from rdflib.term import Node

# Type definitions
ShapeProperty = Tuple[URIRef, Union[URIRef, XSD], int, Optional[int]]
ClassDefinition = Tuple[URIRef, str, str]
PropertyDefinition = Tuple[URIRef, str, Optional[URIRef], URIRef]

class TemplateOntology(Ontology):
    """Template class providing common SHACL patterns and validation functionality."""

    def __init__(self, base_uri: str):
        """Initialize the template ontology.
        
        Args:
            base_uri: Base URI for the ontology
        """
        super().__init__(base_uri)

    def add_shape(self, shape_uri: URIRef, target_class: URIRef, properties: List[ShapeProperty]) -> None:
        """Add a SHACL shape to the ontology.
        
        Args:
            shape_uri: URI of the shape
            target_class: Class that the shape targets
            properties: List of property constraints
        """
        self.graph.add((shape_uri, RDF.type, SH.NodeShape))
        self.graph.add((shape_uri, SH.targetClass, target_class))
        
        for prop, datatype, min_count, max_count in properties:
            constraint = BNode()
            self.graph.add((shape_uri, SH.property, constraint))
            self.graph.add((constraint, SH.path, prop))
            self.graph.add((constraint, SH.minCount, Literal(min_count)))
            if max_count:
                self.graph.add((constraint, SH.maxCount, Literal(max_count)))
            if datatype:
                if datatype in [XSD.string, XSD.boolean, XSD.integer]:
                    self.graph.add((constraint, SH.datatype, datatype))
                else:
                    self.graph.add((constraint, SH['class'], datatype))

    def add_class_hierarchy(self, classes: List[ClassDefinition], 
                          properties: List[PropertyDefinition],
                          subclass_relations: List[Tuple[URIRef, URIRef]] = None) -> None:
        """Add a class hierarchy with properties to the ontology.
        
        Args:
            classes: List of (uri, label, comment) tuples defining classes
            properties: List of (uri, label, domain, range) tuples defining properties
            subclass_relations: Optional list of (subclass, superclass) pairs
        """
        # Add classes
        for class_uri, label, comment in classes:
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(label)))
            self.graph.add((class_uri, RDFS.comment, Literal(comment)))

        # Add properties
        for prop_uri, label, domain, range_uri in properties:
            prop_type = OWL.DatatypeProperty if range_uri in [XSD.string, XSD.boolean, XSD.integer] else OWL.ObjectProperty
            self.graph.add((prop_uri, RDF.type, prop_type))
            self.graph.add((prop_uri, RDFS.label, Literal(label)))
            if domain:
                self.graph.add((prop_uri, RDFS.domain, domain))
            if range_uri:
                self.graph.add((prop_uri, RDFS.range, range_uri))

        # Add subclass relations
        if subclass_relations:
            for subclass, superclass in subclass_relations:
                self.graph.add((subclass, RDFS.subClassOf, superclass))

    def add_individual(self, uri: URIRef, type_uri: URIRef, label: str, 
                      string_rep: str, properties: Dict[URIRef, Any] = None) -> None:
        """Add an individual to the ontology with its properties.
        
        Args:
            uri: URI of the individual
            type_uri: Type (class) of the individual
            label: Label for the individual
            string_rep: String representation
            properties: Dictionary of property URIs to values
        """
        self.graph.add((uri, RDF.type, type_uri))
        self.graph.add((uri, RDFS.label, Literal(label)))
        
        if hasattr(self, 'hasStringRepresentation'):
            self.graph.add((uri, self.hasStringRepresentation, Literal(string_rep)))
        
        if properties:
            for prop_uri, value in properties.items():
                if isinstance(value, bool):
                    self.graph.add((uri, prop_uri, Literal(value)))
                elif isinstance(value, int):
                    self.graph.add((uri, prop_uri, Literal(value)))
                elif isinstance(value, URIRef):
                    self.graph.add((uri, prop_uri, value))
                else:
                    self.graph.add((uri, prop_uri, Literal(str(value)))) 