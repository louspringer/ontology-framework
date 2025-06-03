"""Compliance ontology module."""

from pathlib import Path
from typing import Union
from rdflib import (
    Graph,
    RDF,
    RDFS,
    OWL,
    URIRef,
    Literal
)
from .base_ontology import BaseOntology

class ComplianceOntology(BaseOntology):
    """Compliance ontology class.
    
    This class handles the compliance ontology, which defines core RDF/RDFS properties
    with metadata for maintaining consistency across all ontologies.
    """
    
    def __init__(self, base_uri: str = "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/compliance#") -> None:
        """Initialize the compliance ontology.
        
        Args:
            base_uri: Base URI for the compliance ontology. Defaults to the compliance module URI.
        """
        super().__init__(base_uri)
        self._add_compliance_definitions()
        
    def _add_compliance_definitions(self) -> None:
        """Add compliance definitions to the ontology graph."""
        # Add RDF type property definition
        self.graph.add((RDF.type, RDFS.label, Literal("22-rdf-syntax-ns# type")))
        self.graph.add((RDF.type, RDFS.comment, Literal("Description of 22-rdf-syntax-ns# type")))
        self.graph.add((RDF.type, RDFS.domain, OWL.Thing))
        self.graph.add((RDF.type, RDFS.range, OWL.Thing))
        self.graph.add((RDF.type, OWL.versionInfo, Literal("1.0.0")))
        
        # Add RDFS subClassOf property definition
        self.graph.add((RDFS.subClassOf, RDFS.label, Literal("rdf-schema# subClassOf")))
        self.graph.add((RDFS.subClassOf, RDFS.comment, Literal("Description of rdf-schema# subClassOf")))
        self.graph.add((RDFS.subClassOf, RDFS.domain, OWL.Thing))
        self.graph.add((RDFS.subClassOf, RDFS.range, OWL.Thing))
        self.graph.add((RDFS.subClassOf, OWL.versionInfo, Literal("1.0.0")))
        
    def emit(self, output_path: Union[str, Path] = "guidance/modules/compliance.ttl") -> None:
        """Emit the compliance ontology to a Turtle file.
        
        Args:
            output_path: Path to save the ontology to. Defaults to "guidance/modules/compliance.ttl".
        """
        # Add ontology metadata
        base_uri = URIRef(self.base_uri)
        self.graph.add((base_uri, RDF.type, OWL.Ontology))
        self.graph.add((base_uri, RDFS.label, Literal("Compliance Ontology", lang="en")))
        self.graph.add((base_uri, RDFS.comment, Literal("Core RDF/RDFS property definitions with metadata", lang="en")))
        self.graph.add((base_uri, OWL.versionInfo, Literal("1.0.0")))
        
        # Save to file
        self.save(output_path) 