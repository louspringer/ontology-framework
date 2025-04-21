from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SH
from typing import Optional, List

class MetaMetaOntology:
    """Class for managing meta-meta level ontology information and validation."""
    
    def __init__(self):
        self.graph = Graph()
        self._setup_namespaces()
        
    def _setup_namespaces(self):
        """Set up common namespaces used in the meta-meta ontology."""
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("sh", SH)
        
    def add_shape(self, shape_uri: URIRef, target_class: URIRef, 
                 properties: List[dict], message: Optional[str] = None):
        """Add a SHACL shape to the meta-meta ontology."""
        self.graph.add((shape_uri, RDF.type, SH.NodeShape))
        self.graph.add((shape_uri, SH.targetClass, target_class))
        
        if message:
            self.graph.add((shape_uri, SH.message, Literal(message)))
            
        for prop in properties:
            prop_node = self.graph.resource(shape_uri + "/property")
            self.graph.add((shape_uri, SH.property, prop_node))
            
            if "path" in prop:
                self.graph.add((prop_node, SH.path, prop["path"]))
            if "minCount" in prop:
                self.graph.add((prop_node, SH.minCount, Literal(prop["minCount"])))
            if "maxCount" in prop:
                self.graph.add((prop_node, SH.maxCount, Literal(prop["maxCount"])))
            if "datatype" in prop:
                self.graph.add((prop_node, SH.datatype, prop["datatype"]))
            if "message" in prop:
                self.graph.add((prop_node, SH.message, Literal(prop["message"])))
                
    def add_rule(self, rule_uri: URIRef, condition: str, action: str):
        """Add a rule to the meta-meta ontology."""
        self.graph.add((rule_uri, RDF.type, SH.Rule))
        self.graph.add((rule_uri, SH.condition, Literal(condition)))
        self.graph.add((rule_uri, SH.action, Literal(action)))
        
    def serialize(self, format: str = "turtle") -> str:
        """Serialize the meta-meta ontology to the specified format."""
        return self.graph.serialize(format=format) 