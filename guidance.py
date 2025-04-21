from typing import List, Dict, Optional, Set, Tuple
from rdflib import Graph, RDF, OWL, RDFS, Namespace, SH, Literal, URIRef, Node
from rdflib.namespace import XSD
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class OntologyClass:
    uri: URIRef
    label: str
    comment: str
    subclasses: List['OntologyClass'] = field(default_factory=list)

@dataclass
class OntologyProperty:
    uri: URIRef
    label: str
    comment: str
    domain: Optional[URIRef] = None
    range: Optional[URIRef] = None

@dataclass
class SHACLShape:
    uri: URIRef
    label: str
    comment: str
    target_class: URIRef
    properties: List[Dict] = field(default_factory=list)

@dataclass
class OntologyIndividual:
    uri: URIRef
    type: URIRef
    label: str
    comment: str

class GuidanceOntology:
    def __init__(self, ontology_path: str = "guidance.ttl") -> None:
        self.graph = Graph()
        self.graph.parse(ontology_path, format="turtle")
        self.GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
        
    def get_classes(self) -> List[OntologyClass]:
        """Get all classes defined in the guidance ontology."""
        classes = []
        for s, _, _ in self.graph.triples((None, RDF.type, OWL.Class)):
            label = next(self.graph.objects(s, RDFS.label), None)
            comment = next(self.graph.objects(s, RDFS.comment), None)
            classes.append(OntologyClass(
                uri=URIRef(str(s)),
                label=str(label) if label else "",
                comment=str(comment) if comment else ""
            ))
        return classes
    
    def get_properties(self) -> List[OntologyProperty]:
        """Get all properties defined in the guidance ontology."""
        properties = []
        for s, _, _ in self.graph.triples((None, RDF.type, OWL.ObjectProperty)):
            label = next(self.graph.objects(s, RDFS.label), None)
            comment = next(self.graph.objects(s, RDFS.comment), None)
            domain = next(self.graph.objects(s, RDFS.domain), None)
            range_ = next(self.graph.objects(s, RDFS.range), None)
            properties.append(OntologyProperty(
                uri=URIRef(str(s)),
                label=str(label) if label else "",
                comment=str(comment) if comment else "",
                domain=URIRef(str(domain)) if domain else None,
                range=URIRef(str(range_)) if range_ else None
            ))
        return properties
    
    def get_shacl_shapes(self) -> List[SHACLShape]:
        """Get all SHACL shapes defined in the guidance ontology."""
        shapes = []
        for s, _, _ in self.graph.triples((None, RDF.type, SH.NodeShape)):
            label = next(self.graph.objects(s, RDFS.label), None)
            comment = next(self.graph.objects(s, RDFS.comment), None)
            target_class = next(self.graph.objects(s, SH.targetClass), None)
            properties = []
            for _, _, prop in self.graph.triples((s, SH.property, None)):
                prop_dict = {}
                for p, o in self.graph.predicate_objects(prop):
                    prop_dict[str(p)] = str(o)
                properties.append(prop_dict)
            shapes.append(SHACLShape(
                uri=URIRef(str(s)),
                label=str(label) if label else "",
                comment=str(comment) if comment else "",
                target_class=URIRef(str(target_class)) if target_class else URIRef(""),
                properties=properties
            ))
        return shapes
    
    def get_individuals(self) -> List[OntologyIndividual]:
        """Get all individuals defined in the guidance ontology."""
        individuals = []
        for s, _, o in self.graph.triples((None, RDF.type, None)):
            if o not in [OWL.Class, OWL.ObjectProperty, SH.NodeShape]:
                label = next(self.graph.objects(s, RDFS.label), None)
                comment = next(self.graph.objects(s, RDFS.comment), None)
                individuals.append(OntologyIndividual(
                    uri=URIRef(str(s)),
                    type=URIRef(str(o)),
                    label=str(label) if label else "",
                    comment=str(comment) if comment else ""
                ))
        return individuals
    
    def get_test_protocols(self) -> List[OntologyIndividual]:
        """Get all test protocols defined in the guidance ontology."""
        return [ind for ind in self.get_individuals() 
                if ind.type == self.GUIDANCE.TestProtocol]
    
    def get_validation_patterns(self) -> List[OntologyIndividual]:
        """Get all validation patterns defined in the guidance ontology."""
        return [ind for ind in self.get_individuals() 
                if ind.type == self.GUIDANCE.ValidationPattern]
    
    def get_todo_items(self) -> List[OntologyIndividual]:
        """Get all TODO items defined in the guidance ontology."""
        return [ind for ind in self.get_individuals() 
                if ind.type == self.GUIDANCE.TODO]
    
    def get_conformance_levels(self) -> List[str]:
        """Get all valid conformance levels defined in the guidance ontology."""
        levels = set()
        for s, _, _ in self.graph.triples((None, RDF.type, self.GUIDANCE.ModelConformance)):
            level = next(self.graph.objects(s, self.GUIDANCE.conformanceLevel), None)
            if level:
                levels.add(str(level))
        return list(levels)
    
    def validate_conformance_level(self, level: str) -> bool:
        """Validate if a given conformance level is valid according to the ontology."""
        return level in self.get_conformance_levels()
    
    def get_test_requirements(self) -> Dict[str, bool]:
        """Get test protocol requirements from the guidance ontology."""
        requirements = {}
        for s, _, _ in self.graph.triples((None, RDF.type, self.GUIDANCE.TestProtocol)):
            prefix_val = next(self.graph.objects(s, self.GUIDANCE.requiresPrefixValidation), None)
            ns_val = next(self.graph.objects(s, self.GUIDANCE.requiresNamespaceValidation), None)
            if prefix_val is not None:
                requirements["requires_prefix_validation"] = bool(prefix_val)
            if ns_val is not None:
                requirements["requires_namespace_validation"] = bool(ns_val)
        return requirements

    def emit_ontology(self, output_path: Optional[str] = None) -> str:
        """
        Serialize the ontology graph to Turtle format.
        
        Args:
            output_path: Optional path to save the serialized ontology. If None, returns the serialized string.
            
        Returns:
            The serialized ontology in Turtle format if output_path is None, otherwise an empty string.
        """
        serialized = self.graph.serialize(format="turtle")
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(serialized)
            return ""
            
        return serialized 