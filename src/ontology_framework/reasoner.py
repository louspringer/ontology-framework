"""Ontology reasoner module providing OWL and SHACL reasoning capabilities."""

from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from datetime import datetime
import logging
import re
from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF, RDFS, OWL, XSD, SH, Node
from rdflib.namespace import NamespaceManager
from rdflib.query import Result, ResultRow
from .exceptions import ReasonerError

logger = logging.getLogger(__name__)

class ReasonerResult:
    """Result of a reasoning operation."""
    
    def __init__(
        self,
        success: bool,
        inferred_triples: List[Tuple[Union[URIRef, BNode, Node], URIRef, Union[URIRef, Literal, BNode]]],
        warnings: List[str],
        errors: List[str],
        execution_time: float,
        timestamp: datetime
    ):
        """Initialize reasoner result.
        
        Args:
            success: Whether reasoning was successful
            inferred_triples: List of inferred triples
            warnings: List of warning messages
            errors: List of error messages
            execution_time: Time taken to execute in seconds
            timestamp: When the reasoning was performed
        """
        self.success = success
        self.inferred_triples = inferred_triples
        self.warnings = warnings
        self.errors = errors
        self.execution_time = execution_time
        self.timestamp = timestamp
        
    def __str__(self) -> str:
        """Get string representation of reasoner result."""
        status = "SUCCESS" if self.success else "FAILURE"
        return (
            f"ReasonerResult[{status}] "
            f"({self.execution_time:.2f}s) - {self.timestamp}"
        )

class OntologyReasoner:
    """Provides OWL and SHACL reasoning capabilities."""
    
    def __init__(self, graph: Optional[Graph] = None):
        """Initialize the reasoner.
        
        Args:
            graph: Optional RDF graph to reason over
        """
        self.graph = graph or Graph()
        self._setup_namespaces()
        
    def _setup_namespaces(self) -> None:
        """Set up common namespaces used in reasoning."""
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        self.graph.bind("sh", SH)
        
    def load_ontology(self, file_path: Union[str, Path]) -> None:
        """Load an ontology from a file.
        
        Args:
            file_path: Path to the ontology file
        """
        self.graph.parse(file_path, format="turtle")
        
    def save_ontology(self, file_path: Union[str, Path]) -> None:
        """Save the ontology to a file.
        
        Args:
            file_path: Path to save the ontology to
        """
        self.graph.serialize(file_path, format="turtle")
        
    def reason(self, rules: Optional[List[str]] = None) -> ReasonerResult:
        """Perform reasoning over the ontology.
        
        Args:
            rules: Optional list of custom reasoning rules
            
        Returns:
            Reasoner result containing inferred triples and messages
        """
        start_time = datetime.now()
        inferred_triples: List[Tuple[Union[URIRef, BNode, Node], URIRef, Union[URIRef, Literal, BNode]]] = []
        warnings: List[str] = []
        errors: List[str] = []
        
        try:
            # Apply OWL reasoning rules
            self._apply_owl_rules(inferred_triples, warnings)
            
            # Apply SHACL reasoning rules
            self._apply_shacl_rules(inferred_triples, warnings)
            
            # Apply custom rules if provided
            if rules:
                self._apply_custom_rules(rules, inferred_triples, warnings)
                
            # Add inferred triples to graph
            for triple in inferred_triples:
                self.graph.add(triple)
                
            execution_time = (datetime.now() - start_time).total_seconds()
            return ReasonerResult(
                success=True,
                inferred_triples=inferred_triples,
                warnings=warnings,
                errors=errors,
                execution_time=execution_time,
                timestamp=start_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            errors.append(str(e))
            return ReasonerResult(
                success=False,
                inferred_triples=inferred_triples,
                warnings=warnings,
                errors=errors,
                execution_time=execution_time,
                timestamp=start_time
            )
            
    def _apply_owl_rules(self, inferred_triples: List[Tuple[Union[URIRef, BNode, Node], URIRef, Union[URIRef, Literal, BNode]]], warnings: List[str]) -> None:
        """Apply OWL reasoning rules.
        
        Args:
            inferred_triples: List to store inferred triples
            warnings: List to store warning messages
        """
        # Apply subclass transitivity
        for s, p, o in self.graph.triples((None, RDFS.subClassOf, None)):
            for s2, p2, o2 in self.graph.triples((o, RDFS.subClassOf, None)):
                inferred_triples.append((s, RDFS.subClassOf, o2))
                
        # Apply property characteristics
        for prop in self.graph.subjects(RDF.type, OWL.TransitiveProperty):
            for s, p, o in self.graph.triples((None, prop, None)):
                for s2, p2, o2 in self.graph.triples((o, prop, None)):
                    inferred_triples.append((s, prop, o2))
                    
        # Apply inverse properties
        for prop in self.graph.subjects(RDF.type, OWL.ObjectProperty):
            for inv_prop in self.graph.objects(prop, OWL.inverseOf):
                for s, p, o in self.graph.triples((None, prop, None)):
                    inferred_triples.append((o, inv_prop, s))
                    
    def _apply_shacl_rules(self, inferred_triples: List[Tuple[Union[URIRef, BNode, Node], URIRef, Union[URIRef, Literal, BNode]]], warnings: List[str]) -> None:
        """Apply SHACL reasoning rules.
        
        Args:
            inferred_triples: List to store inferred triples
            warnings: List to store warning messages
        """
        # Apply property constraints
        for shape in self.graph.subjects(RDF.type, SH.NodeShape):
            target_class = self.graph.value(shape, SH.targetClass)
            if target_class:
                for prop in self.graph.objects(shape, SH.property):
                    path = self.graph.value(prop, SH.path)
                    if path:
                        # Apply cardinality constraints
                        min_count = self.graph.value(prop, SH.minCount)
                        max_count = self.graph.value(prop, SH.maxCount)
                        if min_count or max_count:
                            for instance in self.graph.subjects(RDF.type, target_class):
                                count = len(list(self.graph.triples((instance, path, None))))
                                if min_count and count < int(str(min_count)):
                                    warnings.append(f"Instance {instance} violates minCount constraint for {path}")
                                if max_count and count > int(str(max_count)):
                                    warnings.append(f"Instance {instance} violates maxCount constraint for {path}")
                                    
                        # Apply value type constraints
                        node_kind = self.graph.value(prop, SH.nodeKind)
                        if node_kind:
                            for instance in self.graph.subjects(RDF.type, target_class):
                                for _, _, value in self.graph.triples((instance, path, None)):
                                    if node_kind == SH.IRI and not isinstance(value, URIRef):
                                        warnings.append(f"Value {value} should be an IRI for {path}")
                                    elif node_kind == SH.Literal and not isinstance(value, Literal):
                                        warnings.append(f"Value {value} should be a literal for {path}")
                                        
                        # Apply datatype constraints
                        datatype = self.graph.value(prop, SH.datatype)
                        if datatype:
                            for instance in self.graph.subjects(RDF.type, target_class):
                                for _, _, value in self.graph.triples((instance, path, None)):
                                    if isinstance(value, Literal) and value.datatype != datatype:
                                        warnings.append(f"Value {value} has incorrect datatype for {path}")
                                        
    def _apply_custom_rules(self, rules: List[str], inferred_triples: List[Tuple[Union[URIRef, BNode, Node], URIRef, Union[URIRef, Literal, BNode]]], warnings: List[str]) -> None:
        """Apply custom reasoning rules.
        
        Args:
            rules: List of custom rules to apply
            inferred_triples: List to store inferred triples
            warnings: List to store warning messages
        """
        for rule in rules:
            try:
                # Parse rule using simple IF-THEN format
                match = re.match(r"IF\s+(.+)\s+THEN\s+(.+)", rule.strip())
                if not match:
                    warnings.append(f"Failed to parse custom rule: {rule}")
                    continue
                    
                condition, conclusion = match.groups()
                
                # Parse condition triple pattern
                condition_parts = condition.strip().split()
                if len(condition_parts) != 3:
                    warnings.append(f"Invalid condition in rule: {condition}")
                    continue
                    
                # Parse conclusion triple pattern
                conclusion_parts = conclusion.strip().split()
                if len(conclusion_parts) != 3:
                    warnings.append(f"Invalid conclusion in rule: {conclusion}")
                    continue
                    
                # Find matches for condition
                for s, p, o in self.graph.triples((None, None, None)):
                    if str(p) == condition_parts[1]:
                        # Create conclusion triple
                        if conclusion_parts[0] == "?x":
                            subject: Union[URIRef, BNode, Node] = s
                        else:
                            subject = URIRef(conclusion_parts[0])
                            
                        predicate = URIRef(conclusion_parts[1])
                        
                        # Handle object based on its type
                        if conclusion_parts[2].startswith('"') and conclusion_parts[2].endswith('"'):
                            obj: Union[URIRef, Literal, BNode] = Literal(conclusion_parts[2][1:-1])
                        else:
                            obj = URIRef(conclusion_parts[2])
                            
                        inferred_triples.append((subject, predicate, obj))
                        
            except Exception as e:
                warnings.append(f"Failed to apply custom rule: {str(e)}")
                
    def validate(self) -> Dict[str, Union[bool, List[str]]]:
        """Validate the ontology using SHACL.
        
        Returns:
            Dictionary with validation results
        """
        issues = []
        is_valid = True
        
        # Check for undefined classes
        for class_uri in self.graph.subjects(RDF.type, OWL.Class):
            if not any(self.graph.triples((class_uri, RDFS.subClassOf, None))):
                is_valid = False
                issues.append(f"Class has no superclass: {class_uri}")
                
        # Check for undefined properties
        for prop in self.graph.subjects(RDF.type, OWL.DatatypeProperty):
            if not any(self.graph.triples((prop, RDFS.domain, None))):
                is_valid = False
                issues.append(f"Property has no domain: {prop}")
            if not any(self.graph.triples((prop, RDFS.range, None))):
                is_valid = False
                issues.append(f"Property has no range: {prop}")
                
        return {
            "is_valid": is_valid,
            "issues": issues
        } 