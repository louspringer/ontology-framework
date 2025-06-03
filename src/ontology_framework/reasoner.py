"""Ontology reasoner module providing OWL and SHACL reasoning capabilities."""

from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from datetime import datetime
import logging
import re
from rdflib import (
    Graph,
    URIRef,
    Literal,
    BNode,
    Namespace,
    RDF,
    RDFS,
    OWL,
    XSD,
    SH
)
from rdflib.namespace import NamespaceManager
from rdflib.query import Result, ResultRow
from .exceptions import ReasonerError

logger = logging.getLogger(__name__)

class ReasonerResult:
    """Result of a reasoning operation."""
    
    def __init__(
        self,
        success: bool,
        inferred_triples: List[Tuple[Union[URIRef, BNode], URIRef, Union[URIRef, Literal, BNode]]],
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
        inferred_triples: List[Tuple[Union[URIRef, BNode], URIRef, Union[URIRef, Literal, BNode]]] = []
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
            
    def _apply_owl_rules(self, inferred_triples: List[Tuple[Union[URIRef, BNode], URIRef, Union[URIRef, Literal, BNode]]], warnings: List[str]) -> None:
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
                    
    def _apply_shacl_rules(self, inferred_triples: List[Tuple[Union[URIRef, BNode], URIRef, Union[URIRef, Literal, BNode]]], warnings: List[str]) -> None:
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
                                        
    def _apply_custom_rules(self, rules: List[str], inferred_triples: List[Tuple[Union[URIRef, BNode], URIRef, Union[URIRef, Literal, BNode]]], warnings: List[str]) -> None:
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
                    
                # Apply rule (simplified implementation)
                cond_s, cond_p, cond_o = condition_parts
                conc_s, conc_p, conc_o = conclusion_parts
                
                # Convert string patterns to URIRefs or literals
                for s, p, o in self.graph.triples((
                    URIRef(cond_s) if cond_s.startswith("http") else None,
                    URIRef(cond_p) if cond_p.startswith("http") else None,
                    URIRef(cond_o) if cond_o.startswith("http") else None
                )):
                    # Add conclusion triple
                    new_s = URIRef(conc_s) if conc_s.startswith("http") else s
                    new_p = URIRef(conc_p) if conc_p.startswith("http") else p
                    new_o = URIRef(conc_o) if conc_o.startswith("http") else o
                    inferred_triples.append((new_s, new_p, new_o))
                    
            except Exception as e:
                warnings.append(f"Error applying custom rule '{rule}': {str(e)}")
                
    def validate(self) -> Dict[str, Union[bool, List[str]]]:
        """Validate the ontology for consistency.
        
        Returns:
            Dictionary containing validation results
        """
        validation_results = {
            "is_consistent": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check for basic consistency violations
            # Check for class cycles
            for cls in self.graph.subjects(RDF.type, OWL.Class):
                if self._has_class_cycle(cls):
                    validation_results["is_consistent"] = False
                    validation_results["errors"].append(f"Class cycle detected involving {cls}")
                    
            # Check for property domain/range violations
            for prop in self.graph.subjects(RDF.type, OWL.ObjectProperty):
                domain = self.graph.value(prop, RDFS.domain)
                range_val = self.graph.value(prop, RDFS.range)
                
                if domain and range_val:
                    for s, p, o in self.graph.triples((None, prop, None)):
                        # Check domain constraint
                        if not list(self.graph.triples((s, RDF.type, domain))):
                            validation_results["warnings"].append(
                                f"Subject {s} of property {prop} may not satisfy domain constraint {domain}"
                            )
                        # Check range constraint
                        if not list(self.graph.triples((o, RDF.type, range_val))):
                            validation_results["warnings"].append(
                                f"Object {o} of property {prop} may not satisfy range constraint {range_val}"
                            )
            
            # Check for undefined properties without domains or ranges
            issues = []
            for prop in self.graph.subjects(RDF.type, OWL.DatatypeProperty):
                if not any(self.graph.triples((prop, RDFS.domain, None))):
                    validation_results["is_consistent"] = False
                    issues.append(f"Property has no domain: {prop}")
                if not any(self.graph.triples((prop, RDFS.range, None))):
                    validation_results["is_consistent"] = False
                    issues.append(f"Property has no range: {prop}")
                             
        except Exception as e:
            validation_results["is_consistent"] = False
            validation_results["errors"].append(f"Validation error: {str(e)}")
            
        # For backward compatibility, add the old keys
        validation_results["is_valid"] = validation_results["is_consistent"]
        validation_results["issues"] = validation_results["errors"] + validation_results["warnings"] + (issues if 'issues' in locals() else [])
            
        return validation_results
        
    def _has_class_cycle(self, cls: URIRef, visited: Optional[set] = None) -> bool:
        """Check if a class has a cycle in its subclass hierarchy.
        
        Args:
            cls: Class to check for cycles
            visited: Set of already visited classes
            
        Returns:
            True if a cycle is detected
        """
        if visited is None:
            visited = set()
            
        if cls in visited:
            return True
            
        visited.add(cls)
        
        for _, _, superclass in self.graph.triples((cls, RDFS.subClassOf, None)):
            if self._has_class_cycle(superclass, visited.copy()):
                return True
                
        return False 