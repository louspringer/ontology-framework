"""
Meta-level ontology information and patch management.
"""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL

from .ontology_types import PatchType, PatchStatus

# Define namespaces
META = Namespace("http://example.org/meta#")

@dataclass
class OntologyPatch:
    """Class representing an ontology patch."""
    patch_id: str
    patch_type: PatchType
    target_ontology: str
    content: str
    status: PatchStatus = PatchStatus.PENDING
    created_at: str = ""
    updated_at: str = ""
    changes: List[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Initialize default values after dataclass initialization."""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if self.changes is None:
            self.changes = []

    def to_rdf(self) -> Graph:
        """Convert patch to RDF graph."""
        g = Graph()
        g.bind("meta", META)
        
        patch_uri = URIRef(f"{META}patch_{self.patch_id}")
        g.add((patch_uri, RDF.type, META.Patch))
        g.add((patch_uri, META.type, Literal(self.patch_type.value)))
        g.add((patch_uri, META.status, Literal(self.status.value)))
        g.add((patch_uri, META.targetOntology, Literal(self.target_ontology)))
        g.add((patch_uri, META.content, Literal(self.content)))
        g.add((patch_uri, META.createdAt, Literal(self.created_at)))
        g.add((patch_uri, META.updatedAt, Literal(self.updated_at)))
            
        if self.changes:
            for i, change in enumerate(self.changes):
                change_uri = URIRef(f"{META}change_{self.patch_id}_{i}")
                g.add((change_uri, RDF.type, META.Change))
                g.add((patch_uri, META.hasChange, change_uri))
                
                for key, value in change.items():
                    g.add((change_uri, META[key], Literal(str(value))))
                    
        return g

class MetaOntology:
    """Class for managing meta-level ontology information."""
    
    def __init__(self) -> None:
        self.graph = Graph()
        self._setup_namespaces()
        
    def _setup_namespaces(self) -> None:
        """Set up common namespaces used in the meta ontology."""
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("meta", META)
        
    def add_class(self, class_uri: URIRef, label: str, comment: Optional[str] = None) -> None:
        """Add a class to the meta ontology."""
        self.graph.add((class_uri, RDF.type, OWL.Class))
        self.graph.add((class_uri, RDFS.label, Literal(label)))
        if comment:
            self.graph.add((class_uri, RDFS.comment, Literal(comment)))
            
    def add_property(self, prop_uri: URIRef, label: str, domain: Optional[URIRef] = None, 
                    range: Optional[URIRef] = None, comment: Optional[str] = None) -> None:
        """Add a property to the meta ontology."""
        self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
        self.graph.add((prop_uri, RDFS.label, Literal(label)))
        if domain:
            self.graph.add((prop_uri, RDFS.domain, domain))
        if range:
            self.graph.add((prop_uri, RDFS.range, range))
        if comment:
            self.graph.add((prop_uri, RDFS.comment, Literal(comment)))
            
    def serialize(self, format: str = "turtle") -> str:
        """Serialize the meta ontology to the specified format."""
        return self.graph.serialize(format=format) 