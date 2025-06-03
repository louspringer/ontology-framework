"""
Module, for transforming, ontologies using the bow-tie pattern.
"""

from typing import Dict, List, Optional, Any, Set
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
from rdflib.term import Node

class BowTieTransformation:
    """Class, for transforming, ontologies using the bow-tie pattern."""
    
    def __init__(self, graph: Graph) -> None:
        """Initialize the transformer with an RDF graph."""
        self.graph = graph
        self.bt_ns = Namespace("https://github.com/louspringer/ontology-framework/bow-tie# ")
        self.graph.bind("bt", self.bt_ns)
        
    def transform(self) -> Graph:
        """Transform the ontology using the bow-tie pattern."""
        transformed_graph = Graph()
        for triple in self.graph:
            transformed_graph.add(triple)
        # Add bow-tie pattern structure
        transformed_graph.add((self.bt_ns.Transformation, RDF.type, OWL.Class))
        transformed_graph.add((self.bt_ns.Transformation, RDFS.label, Literal("Transformation", lang="en")))
        transformed_graph.add((self.bt_ns.Transformation, RDFS.comment, Literal("A transformation process", lang="en")))
        transformed_graph.add((self.bt_ns.Input, RDF.type, OWL.Class))
        transformed_graph.add((self.bt_ns.Input, RDFS.label, Literal("Input", lang="en")))
        transformed_graph.add((self.bt_ns.Input, RDFS.comment, Literal("Input to a transformation", lang="en")))
        transformed_graph.add((self.bt_ns.Output, RDF.type, OWL.Class))
        transformed_graph.add((self.bt_ns.Output, RDFS.label, Literal("Output", lang="en")))
        transformed_graph.add((self.bt_ns.Output, RDFS.comment, Literal("Output from a transformation", lang="en")))
        transformed_graph.add((self.bt_ns.hasInput, RDF.type, OWL.ObjectProperty))
        transformed_graph.add((self.bt_ns.hasInput, RDFS.label, Literal("has input", lang="en")))
        transformed_graph.add((self.bt_ns.hasInput, RDFS.comment, Literal("Links a transformation to its input", lang="en")))
        transformed_graph.add((self.bt_ns.hasInput, RDFS.domain, self.bt_ns.Transformation))
        transformed_graph.add((self.bt_ns.hasInput, RDFS.range, self.bt_ns.Input))
        transformed_graph.add((self.bt_ns.hasOutput, RDF.type, OWL.ObjectProperty))
        transformed_graph.add((self.bt_ns.hasOutput, RDFS.label, Literal("has output", lang="en")))
        transformed_graph.add((self.bt_ns.hasOutput, RDFS.comment, Literal("Links a transformation to its output", lang="en")))
        transformed_graph.add((self.bt_ns.hasOutput, RDFS.domain, self.bt_ns.Transformation))
        transformed_graph.add((self.bt_ns.hasOutput, RDFS.range, self.bt_ns.Output))
        transformation_shape = BNode()
        transformed_graph.add((transformation_shape, RDF.type, SH.NodeShape))
        transformed_graph.add((transformation_shape, SH.targetClass, self.bt_ns.Transformation))
        input_property = BNode()
        transformed_graph.add((input_property, SH.path, self.bt_ns.hasInput))
        transformed_graph.add((input_property, SH.minCount, Literal(1, datatype=XSD.integer)))
        transformed_graph.add((input_property, SH.maxCount, Literal(1, datatype=XSD.integer)))
        transformed_graph.add((transformation_shape, SH.property, input_property))
        output_property = BNode()
        transformed_graph.add((output_property, SH.path, self.bt_ns.hasOutput))
        transformed_graph.add((output_property, SH.minCount, Literal(1, datatype=XSD.integer)))
        transformed_graph.add((output_property, SH.maxCount, Literal(1, datatype=XSD.integer)))
        transformed_graph.add((transformation_shape, SH.property, output_property))
        transformed_graph.bind("bt", self.bt_ns)
        return transformed_graph
        
    def validate(self) -> bool:
        """Check if the graph follows the bow-tie pattern."""
        required_classes = {
            self.bt_ns.Transformation,
            self.bt_ns.Input,
            self.bt_ns.Output
        }
        for cls in required_classes:
            if not (cls, RDF.type, OWL.Class) in self.graph:
                return False
        required_properties = {
            self.bt_ns.hasInput,
            self.bt_ns.hasOutput
        }
        for prop in required_properties:
            if not (prop, RDF.type, OWL.ObjectProperty) in self.graph:
                return False
        if not (self.bt_ns.hasInput, RDFS.domain, self.bt_ns.Transformation) in self.graph:
            return False
        if not (self.bt_ns.hasInput, RDFS.range, self.bt_ns.Input) in self.graph:
            return False
        if not (self.bt_ns.hasOutput, RDFS.domain, self.bt_ns.Transformation) in self.graph:
            return False
        if not (self.bt_ns.hasOutput, RDFS.range, self.bt_ns.Output) in self.graph:
            return False
        query = """
        PREFIX bt: <https://github.com/louspringer/ontology-framework/bow-tie#>
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        ASK {
            ?shape a sh:NodeShape .
            ?shape sh:targetClass bt:Transformation .
            ?shape sh:property ?input_property .
            ?input_property sh:path bt:hasInput .
            ?input_property sh:minCount 1 .
            ?input_property sh:maxCount 1 .
            ?shape sh:property ?output_property .
            ?output_property sh:path bt:hasOutput .
            ?output_property sh:minCount 1 .
            ?output_property sh:maxCount 1 .
        }
        """
        return bool(self.graph.query(query).askAnswer) 