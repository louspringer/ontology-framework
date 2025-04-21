"""Module for validating ontology structure and conformance."""

from typing import Dict, List, Optional, Union
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
import logging

# Configure logging
logger = logging.getLogger(__name__)

class OntologyValidator:
    """Class for validating ontology structure and conformance."""
    
    def __init__(self, guidance_graph: Graph) -> None:
        """Initialize the validator with a guidance graph.
        
        Args:
            guidance_graph: The graph containing the guidance ontology
        """
        self.guidance_graph = guidance_graph
        self.GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
        
    def validate_conformance_levels(self) -> Dict[str, List[str]]:
        """Validate the conformance levels in the guidance ontology.
        
        Returns:
            Dict mapping validation results to lists of messages
        """
        results: Dict[str, List[str]] = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check that all required conformance levels exist
        required_levels = ["STRICT", "MODERATE", "RELAXED"]
        for level in required_levels:
            level_uri = self.GUIDANCE[level]
            if not (level_uri, RDF.type, self.GUIDANCE.ConformanceLevel) in self.guidance_graph:
                results["errors"].append(f"Missing required conformance level: {level}")
            
            # Check required properties
            if not any(self.guidance_graph.triples((level_uri, self.GUIDANCE.hasStringRepresentation, None))):
                results["errors"].append(f"Missing string representation for {level}")
            if not any(self.guidance_graph.triples((level_uri, self.GUIDANCE.hasValidationRules, None))):
                results["errors"].append(f"Missing validation rules for {level}")
            if not any(self.guidance_graph.triples((level_uri, self.GUIDANCE.hasMinimumRequirements, None))):
                results["errors"].append(f"Missing minimum requirements for {level}")
            if not any(self.guidance_graph.triples((level_uri, self.GUIDANCE.hasComplianceMetrics, None))):
                results["errors"].append(f"Missing compliance metrics for {level}")
        
        # Check SHACL shape
        shape_uri = self.GUIDANCE.ConformanceLevelShape
        if not (shape_uri, RDF.type, SH.NodeShape) in self.guidance_graph:
            results["errors"].append("Missing SHACL shape for ConformanceLevel")
        
        return results
    
    def validate_integration_process(self) -> Dict[str, List[str]]:
        """Validate the integration process structure.
        
        Returns:
            Dict mapping validation results to lists of messages
        """
        results: Dict[str, List[str]] = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check integration process class
        if not (self.GUIDANCE.IntegrationProcess, RDF.type, OWL.Class) in self.guidance_graph:
            results["errors"].append("Missing IntegrationProcess class definition")
        
        # Check integration step class
        if not (self.GUIDANCE.IntegrationStep, RDF.type, OWL.Class) in self.guidance_graph:
            results["errors"].append("Missing IntegrationStep class definition")
        
        # Check step properties
        if not (self.GUIDANCE.stepOrder, RDF.type, OWL.DatatypeProperty) in self.guidance_graph:
            results["errors"].append("Missing stepOrder property definition")
        if not (self.GUIDANCE.stepDescription, RDF.type, OWL.DatatypeProperty) in self.guidance_graph:
            results["errors"].append("Missing stepDescription property definition")
        
        return results
    
    def validate_test_protocol(self) -> Dict[str, List[str]]:
        """Validate the test protocol structure.
        
        Returns:
            Dict mapping validation results to lists of messages
        """
        results: Dict[str, List[str]] = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check test protocol class
        if not (self.GUIDANCE.TestProtocol, RDF.type, OWL.Class) in self.guidance_graph:
            results["errors"].append("Missing TestProtocol class definition")
        
        # Check test phase class
        if not (self.GUIDANCE.TestPhase, RDF.type, OWL.Class) in self.guidance_graph:
            results["errors"].append("Missing TestPhase class definition")
        
        # Check protocol properties
        if not (self.GUIDANCE.hasTestPhase, RDF.type, OWL.ObjectProperty) in self.guidance_graph:
            results["errors"].append("Missing hasTestPhase property definition")
        if not (self.GUIDANCE.requiresNamespaceValidation, RDF.type, OWL.DatatypeProperty) in self.guidance_graph:
            results["errors"].append("Missing requiresNamespaceValidation property definition")
        if not (self.GUIDANCE.requiresPrefixValidation, RDF.type, OWL.DatatypeProperty) in self.guidance_graph:
            results["errors"].append("Missing requiresPrefixValidation property definition")
        
        return results
    
    def validate_guidance_ontology(self) -> Dict[str, List[str]]:
        """Validate the entire guidance ontology.
        
        Returns:
            Dict mapping validation results to lists of messages
        """
        results: Dict[str, List[str]] = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Validate each component
        conformance_results = self.validate_conformance_levels()
        integration_results = self.validate_integration_process()
        protocol_results = self.validate_test_protocol()
        
        # Combine results
        for key in results:
            results[key].extend(conformance_results[key])
            results[key].extend(integration_results[key])
            results[key].extend(protocol_results[key])
        
        return results 