"""Base class for ontology operations."""

from typing import Dict, List, Optional, Union, Any, TypeVar, Generic
from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF, RDFS, OWL, XSD, SH
from rdflib.namespace import NamespaceManager
from rdflib.query import Result, ResultRow
import glob
from .compliance import ComplianceOntology
from .base_ontology import BaseOntology

T = TypeVar('T')

class Ontology(BaseOntology):
    """Base class for ontology operations.
    
    This class provides common functionality for working with ontologies,
    including type conversion, serialization, and basic SPARQL operations.
    """
    
    def __init__(self, base_uri: str, load_guidance_modules: bool = True) -> None:
        """Initialize the ontology.
        
        Args:
            base_uri: Base URI for the ontology namespace
            load_guidance_modules: Whether to load guidance modules. Defaults to True.
        """
        super().__init__(base_uri)
        
        # Define essential framework classes
        self.IntegrationRequirement = self.base.IntegrationRequirement
        self.SHACLValidation = self.base.SHACLValidation
        self.TODO = self.base.TODO
        self.ValidationPattern = self.base.ValidationPattern
        
        # Define SHACL terms
        self.SH = SH
        self.SH_CLASS = SH['class']
        self.SH_DATATYPE = SH['datatype']
        self.SH_PATH = SH['path']
        self.SH_PROPERTY = SH['property']
        self.SH_MINCOUNT = SH['minCount']
        self.SH_MAXCOUNT = SH['maxCount']
        self.SH_TARGETCLASS = SH['targetClass']
        self.SH_NODESHAPE = SH['NodeShape']
        
        # Add essential framework classes to the graph
        self._add_framework_classes()
        
        # Load guidance modules if requested
        if load_guidance_modules:
            self._load_guidance_modules()
        
    def _load_guidance_modules(self) -> None:
        """Load all guidance modules from the guidance/modules directory."""
        # Load compliance ontology
        compliance = ComplianceOntology()
        self.graph += compliance.graph
        
    def _add_framework_classes(self) -> None:
        """Add essential framework classes to the ontology graph."""
        # IntegrationRequirement class
        self.graph.add((self.IntegrationRequirement, RDF.type, OWL.Class))
        self.graph.add((self.IntegrationRequirement, RDFS.label, Literal("Integration Requirement", lang="en")))
        self.graph.add((self.IntegrationRequirement, RDFS.comment, Literal("Requirements for integrating validation components", lang="en")))
        
        # SHACLValidation class
        self.graph.add((self.SHACLValidation, RDF.type, OWL.Class))
        self.graph.add((self.SHACLValidation, RDFS.label, Literal("SHACL Validation", lang="en")))
        self.graph.add((self.SHACLValidation, RDFS.comment, Literal("Rules and patterns for SHACL validation", lang="en")))
        
        # TODO class
        self.graph.add((self.TODO, RDF.type, OWL.Class))
        self.graph.add((self.TODO, RDFS.label, Literal("Future Improvements")))
        self.graph.add((self.TODO, RDFS.comment, Literal("Items for future development and enhancement")))
        
        # ValidationPattern class
        self.graph.add((self.ValidationPattern, RDF.type, OWL.Class))
        self.graph.add((self.ValidationPattern, RDFS.label, Literal("Validation Pattern", lang="en")))
        self.graph.add((self.ValidationPattern, RDFS.comment, Literal("Pattern for implementing validation rules", lang="en")))
        
    def load(self, file_path: Union[str, Path]) -> None:
        """Load an ontology from a file.
        
        Args:
            file_path: Path to the ontology file.
        """
        self.graph.parse(file_path, format="turtle")
        
    def save(self, file_path: Union[str, Path]) -> None:
        """Save the ontology to a file.
        
        Args:
            file_path: Path to save the ontology to.
        """
        self.graph.serialize(file_path, format="turtle")
        
    def query(self, query: str) -> list:
        """Execute a SPARQL query on the ontology.
        
        Args:
            query: SPARQL query string.
            
        Returns:
            List of query results.
        """
        return list(self.graph.query(query))
        
    def to_python(self, value: URIRef) -> Union[str, int, float, bool, None]:
        """Convert an RDF value to a Python type.
        
        Args:
            value: RDF value to convert.
            
        Returns:
            Python value.
        """
        if isinstance(value, Literal):
            return value.toPython()
        return str(value)
        
    def to_rdf(self, value: Union[str, int, float, bool, None]) -> Union[URIRef, Literal]:
        """Convert a Python value to an RDF type.
        
        Args:
            value: Python value to convert.
            
        Returns:
            RDF value.
        """
        if isinstance(value, (int, float, bool)):
            return Literal(value)
        elif value is None:
            return Literal("")
        return Literal(str(value))
        
    def get_metadata(self) -> Dict[str, Any]:
        """Get ontology metadata.
        
        Returns:
            Dictionary containing ontology metadata
        """
        query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?label ?comment ?version
        WHERE {
            ?ontology rdf:type owl:Ontology ;
                     rdfs:label ?label ;
                     rdfs:comment ?comment ;
                     owl:versionInfo ?version .
        }
        """
        results = self.query(query)
        if results:
            row = next(results)
            return {
                'label': self.to_python(row[0]),
                'comment': self.to_python(row[1]),
                'version': self.to_python(row[2])
            }
        return {}

    def emit_ontology(self, output_path: Union[str, Path] = "ontology.ttl") -> None:
        """Emit the base ontology to a Turtle file.
        
        Args:
            output_path: Path to save the ontology to. Defaults to "ontology.ttl".
        """
        # Add ontology metadata
        base_uri = URIRef(self.base_uri)
        self.graph.add((base_uri, RDF.type, OWL.Ontology))
        self.graph.add((base_uri, RDFS.label, Literal("Base Ontology", lang="en")))
        self.graph.add((base_uri, RDFS.comment, Literal("Core ontology for the ontology framework", lang="en")))
        self.graph.add((base_uri, OWL.versionInfo, Literal("0.1.0")))
        
        # Save to file
        self.save(output_path) 