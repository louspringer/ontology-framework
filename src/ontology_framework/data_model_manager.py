"""
Module for managing ontology data models.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL

@dataclass
class DataModelVersion:
    """Version information for a data model."""
    version: str
    timestamp: datetime
    changes: List[str]
    author: str
    
class DataModelManager:
    """Class for managing ontology data models."""
    
    def __init__(self, base_uri: str):
        """Initialize the manager.
        
        Args:
            base_uri: Base URI for the data model
        """
        self.base_uri = base_uri
        self.graph = Graph()
        self.versions: Dict[str, DataModelVersion] = {}
        
        # Bind common namespaces
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        
    def create_class(self, class_name: str, label: str, comment: str) -> URIRef:
        """Create a new class in the data model.
        
        Args:
            class_name: Name of the class
            label: Human-readable label
            comment: Description of the class
            
        Returns:
            URIRef of the created class
        """
        class_uri = URIRef(f"{self.base_uri}#{class_name}")
        
        self.graph.add((class_uri, RDF.type, OWL.Class))
        self.graph.add((class_uri, RDFS.label, Literal(label)))
        self.graph.add((class_uri, RDFS.comment, Literal(comment)))
        
        return class_uri
        
    def create_property(self, 
                       property_name: str,
                       domain_class: URIRef,
                       range_class: URIRef,
                       label: str,
                       comment: str) -> URIRef:
        """Create a new property in the data model.
        
        Args:
            property_name: Name of the property
            domain_class: Domain class URI
            range_class: Range class URI
            label: Human-readable label
            comment: Description of the property
            
        Returns:
            URIRef of the created property
        """
        property_uri = URIRef(f"{self.base_uri}#{property_name}")
        
        self.graph.add((property_uri, RDF.type, OWL.ObjectProperty))
        self.graph.add((property_uri, RDFS.domain, domain_class))
        self.graph.add((property_uri, RDFS.range, range_class))
        self.graph.add((property_uri, RDFS.label, Literal(label)))
        self.graph.add((property_uri, RDFS.comment, Literal(comment)))
        
        return property_uri
        
    def add_subclass_relationship(self, subclass: URIRef, superclass: URIRef):
        """Add a subclass relationship between two classes.
        
        Args:
            subclass: URI of the subclass
            superclass: URI of the superclass
        """
        self.graph.add((subclass, RDFS.subClassOf, superclass))
        
    def add_equivalent_class(self, class1: URIRef, class2: URIRef):
        """Add an equivalence relationship between two classes.
        
        Args:
            class1: URI of the first class
            class2: URI of the second class
        """
        self.graph.add((class1, OWL.equivalentClass, class2))
        
    def add_disjoint_classes(self, classes: List[URIRef]):
        """Specify that a list of classes are mutually disjoint.
        
        Args:
            classes: List of class URIs to make disjoint
        """
        for i, class1 in enumerate(classes):
            for class2 in classes[i+1:]:
                self.graph.add((class1, OWL.disjointWith, class2))
                
    def create_version(self, version: str, changes: List[str], author: str):
        """Create a new version of the data model.
        
        Args:
            version: Version string (e.g. "1.0.0")
            changes: List of changes made in this version
            author: Name of the author making the changes
        """
        self.versions[version] = DataModelVersion(
            version=version,
            timestamp=datetime.now(),
            changes=changes,
            author=author
        )
        
    def get_version_history(self) -> List[DataModelVersion]:
        """Get the version history of the data model.
        
        Returns:
            List of version information, ordered by timestamp
        """
        return sorted(
            self.versions.values(),
            key=lambda v: v.timestamp
        )
        
    def export_to_file(self, file_path: str, format: str = "turtle"):
        """Export the data model to a file.
        
        Args:
            file_path: Path to save the file
            format: Format to serialize to (default: turtle)
        """
        self.graph.serialize(destination=file_path, format=format)
        
    def import_from_file(self, file_path: str, format: str = "turtle"):
        """Import a data model from a file.
        
        Args:
            file_path: Path to the file to import
            format: Format of the file (default: turtle)
        """
        self.graph.parse(file_path, format=format)
        
    def validate_model(self) -> List[str]:
        """Validate the data model.
        
        Returns:
            List of validation errors, empty if valid
        """
        errors = []
        
        # Check all classes have labels and comments
        for cls in self.graph.subjects(RDF.type, OWL.Class):
            if not any(self.graph.triples((cls, RDFS.label, None))):
                errors.append(f"Class {cls} is missing a label")
            if not any(self.graph.triples((cls, RDFS.comment, None))):
                errors.append(f"Class {cls} is missing a description")
                
        # Check all properties have domain and range
        for prop in self.graph.subjects(RDF.type, OWL.ObjectProperty):
            if not any(self.graph.triples((prop, RDFS.domain, None))):
                errors.append(f"Property {prop} is missing a domain")
            if not any(self.graph.triples((prop, RDFS.range, None))):
                errors.append(f"Property {prop} is missing a range")
                
        return errors 