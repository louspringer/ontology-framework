from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import Optional, List, Dict, Any, TypedDict
import os

from . import SHACL
from pyshacl import validate

class OntologyInfo(TypedDict):
    classes: List[str]
    properties: List[str]
    instances: List[str]

class OntologyManager:
    """Manages ontology operations and validation."""
    
    def __init__(self, ontology_file: str):
        """Initialize the ontology manager with a TTL file.
        
        Args:
            ontology_file: Path to the ontology TTL file
        """
        self.ontology_file = ontology_file
        self.graph = Graph()
        
        # Bind the correct prefixes
        self.graph.bind('rdf', URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
        self.graph.bind('rdfs', URIRef('http://www.w3.org/2000/01/rdf-schema#'))
        self.graph.bind('owl', URIRef('http://www.w3.org/2002/07/owl#'))
        self.graph.bind('xsd', URIRef('http://www.w3.org/2001/XMLSchema#'))
        self.graph.bind('sh', SHACL)
        
        # Parse the ontology file
        self.graph.parse(ontology_file, format='turtle')
        
        # Create namespace for the ontology
        self.ex = Namespace('./stereo#')
        self.graph.bind('ex', self.ex)
    
    def validate_ontology(self) -> List[str]:
        """Validate the ontology using SHACL shapes.
        
        Returns:
            List of validation messages
        """
        validation_messages = []
        
        # Create SHACL shapes graph
        shapes_graph = Graph()
        
        # Problem Space Shape
        problem_shape = BNode()
        shapes_graph.add((problem_shape, RDF.type, SHACL.NodeShape))
        shapes_graph.add((problem_shape, SHACL.targetClass, self.ex.ProblemSpace))
        
        # Add label property constraint
        label_constraint = BNode()
        shapes_graph.add((problem_shape, SHACL.property, label_constraint))
        shapes_graph.add((label_constraint, SHACL.path, RDFS.label))
        shapes_graph.add((label_constraint, SHACL.minCount, Literal(1)))
        shapes_graph.add((label_constraint, SHACL.maxCount, Literal(1)))
        shapes_graph.add((label_constraint, SHACL.datatype, XSD.string))
        
        # Add comment property constraint
        comment_constraint = BNode()
        shapes_graph.add((problem_shape, SHACL.property, comment_constraint))
        shapes_graph.add((comment_constraint, SHACL.path, RDFS.comment))
        shapes_graph.add((comment_constraint, SHACL.minCount, Literal(1)))
        shapes_graph.add((comment_constraint, SHACL.datatype, XSD.string))
        
        # Validate the ontology using pyshacl
        conforms, results_graph, results_text = validate(
            self.graph,
            shacl_graph=shapes_graph,
            ont_graph=None,
            inference='rdfs',
            abort_on_first=False,
            allow_infos=False,
            meta_shacl=False,
            debug=False
        )
        
        if not conforms:
            validation_messages.extend(results_text.split('\n'))
        
        return validation_messages
    
    def get_ontology_info(self) -> OntologyInfo:
        """Get information about the ontology.
        
        Returns:
            Dictionary containing ontology information
        """
        info: OntologyInfo = {
            'classes': [],
            'properties': [],
            'instances': []
        }
        
        # Get classes
        for s, p, o in self.graph.triples((None, RDF.type, OWL.Class)):
            info['classes'].append(str(s))
        
        # Get properties
        for s, p, o in self.graph.triples((None, RDF.type, OWL.ObjectProperty)):
            info['properties'].append(str(s))
        
        # Get instances
        for s, p, o in self.graph.triples((None, RDF.type, None)):
            if str(o) not in [str(OWL.Class), str(OWL.ObjectProperty)]:
                info['instances'].append(str(s))
        
        return info 