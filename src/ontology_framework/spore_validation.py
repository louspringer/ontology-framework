"""SPORE validation functionality for the ontology framework.

This module provides functionality for validating ontologies against SPORE
(Semantic Patterns for Ontology Reuse and Evolution) patterns.
"""

from typing import Dict, List, Optional, Set, Tuple
import logging
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from .exceptions import ValidationError

logger = logging.getLogger(__name__)

class SporeValidator:
    """Validates ontologies against SPORE patterns."""
    
    def __init__(self, ontology_graph: Graph):
        """Initialize SPORE validator.
        
        Args:
            ontology_graph: RDFlib Graph containing the ontology to validate
        """
        self.graph = ontology_graph
        
    def validate_spore(self, spore_uri: URIRef, target_model: URIRef) -> Tuple[bool, List[str]]:
        """Validate a SPORE before integration.
        
        Args:
            spore_uri: URI of the SPORE to validate
            target_model: URI of the target model
            
        Returns:
            Tuple of (is_valid, list of validation messages)
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            messages = []
            is_valid = True
            
            # Check if spore exists and has correct type
            if not any(self.graph.triples((spore_uri, RDF.type, None))):
                is_valid = False
                messages.append(f"SPORE {spore_uri} not found in graph")
                return is_valid, messages
                
            spore_types = list(self.graph.objects(spore_uri, RDF.type))
            if not any(t for t in spore_types if str(t).endswith("#Spore")):
                is_valid = False
                messages.append(f"Invalid SPORE type: {spore_types}")
            
            # Check target model
            spore_target = next(self.graph.objects(spore_uri, URIRef("http://example.org/guidance#targetModel")), None)
            if not spore_target:
                is_valid = False
                messages.append(f"SPORE {spore_uri} has no target model")
            elif spore_target != target_model:
                is_valid = False
                messages.append(f"SPORE target model mismatch: expected {target_model}, got {spore_target}")
            
            # Check for required properties
            required_properties = [
                URIRef("http://example.org/guidance#distributesPatch"),
                OWL.versionInfo,
                RDFS.label,
                RDFS.comment
            ]
            
            for prop in required_properties:
                if not any(self.graph.triples((spore_uri, prop, None))):
                    is_valid = False
                    messages.append(f"Missing required property: {prop}")
            
            # Validate patches
            patches = list(self.graph.objects(spore_uri, URIRef("http://example.org/guidance#distributesPatch")))
            if not patches:
                is_valid = False
                messages.append("No patches found")
            else:
                for patch in patches:
                    patch_type = next(self.graph.objects(patch, RDF.type), None)
                    if not patch_type or not str(patch_type).endswith("#ConceptPatch"):
                        is_valid = False
                        messages.append(f"Invalid patch type for {patch}: {patch_type}")
            
            return is_valid, messages
            
        except Exception as e:
            raise ValidationError(f"SPORE validation failed: {str(e)}")
            
    def validate_pattern(self, pattern_graph: Graph) -> Tuple[bool, List[str]]:
        """Validate ontology against a SPORE pattern.
        
        Args:
            pattern_graph: RDFlib Graph containing the SPORE pattern
            
        Returns:
            Tuple of (is_valid, list of validation messages)
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            messages = []
            is_valid = True
            
            # Check class hierarchy
            pattern_classes = set(pattern_graph.subjects(RDF.type, OWL.Class))
            ontology_classes = set(self.graph.subjects(RDF.type, OWL.Class))
            
            for pattern_class in pattern_classes:
                if pattern_class not in ontology_classes:
                    is_valid = False
                    messages.append(f"Missing class: {pattern_class}")
                    
                # Check properties
                pattern_properties = set(pattern_graph.predicates(pattern_class, None))
                ontology_properties = set(self.graph.predicates(pattern_class, None))
                
                missing_properties = pattern_properties - ontology_properties
                if missing_properties:
                    is_valid = False
                    messages.append(f"Missing properties for {pattern_class}: {missing_properties}")
                    
            # Check property restrictions
            for property_restriction in pattern_graph.subjects(RDF.type, OWL.Restriction):
                if not any(self.graph.triples((None, None, property_restriction))):
                    is_valid = False
                    messages.append(f"Missing property restriction: {property_restriction}")
                    
            return is_valid, messages
            
        except Exception as e:
            raise ValidationError(f"SPORE validation failed: {str(e)}")
            
    def validate_naming_conventions(self) -> Tuple[bool, List[str]]:
        """Validate ontology naming conventions.
        
        Returns:
            Tuple of (is_valid, list of validation messages)
        """
        messages = []
        is_valid = True
        
        # Check class names (should be CamelCase)
        for class_uri in self.graph.subjects(RDF.type, OWL.Class):
            class_name = str(class_uri).split("#")[-1]
            if not class_name[0].isupper() or "_" in class_name:
                is_valid = False
                messages.append(f"Invalid class name (should be CamelCase): {class_name}")
                
        # Check property names (should be camelCase)
        for prop in self.graph.subjects(RDF.type, OWL.DatatypeProperty):
            prop_name = str(prop).split("#")[-1]
            if prop_name[0].isupper() or "_" in prop_name:
                is_valid = False
                messages.append(f"Invalid property name (should be camelCase): {prop_name}")
                
        return is_valid, messages
        
    def validate_documentation(self) -> Tuple[bool, List[str]]:
        """Validate ontology documentation.
        
        Returns:
            Tuple of (is_valid, list of validation messages)
        """
        messages = []
        is_valid = True
        
        # Check for rdfs:label and rdfs:comment
        for subject in self.graph.subjects(RDF.type, OWL.Class):
            if not any(self.graph.triples((subject, RDFS.label, None))):
                is_valid = False
                messages.append(f"Missing rdfs:label for {subject}")
            if not any(self.graph.triples((subject, RDFS.comment, None))):
                is_valid = False
                messages.append(f"Missing rdfs:comment for {subject}")
                
        return is_valid, messages 