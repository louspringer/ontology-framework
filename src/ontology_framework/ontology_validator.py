"""Module for validating ontology structure and conformance."""

from typing import Dict, List, Optional, Union
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH
from pathlib import Path
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
        
    def validate_validation_rules(self) -> Dict[str, List[str]]:
        """Validate the validation rules in the guidance ontology.
        
        Returns:
            Dict mapping validation results to lists of messages
        """
        results: Dict[str, List[str]] = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check that all required validation rule classes exist
        required_classes = ["ValidationRule", "ConsistencyRule", "SemanticRule", "SyntaxRule"]
        for cls in required_classes:
            class_uri = self.GUIDANCE[cls]
            if not (class_uri, RDF.type, OWL.Class) in self.guidance_graph:
                results["errors"].append(f"Missing required class: {cls}")
            
            # Check required properties for ValidationRule
            if cls == "ValidationRule":
                if not any(self.guidance_graph.triples((class_uri, RDFS.label, None))):
                    results["errors"].append(f"Missing label for {cls}")
                if not any(self.guidance_graph.triples((class_uri, RDFS.comment, None))):
                    results["errors"].append(f"Missing comment for {cls}")
        
        # Check that all required properties exist
        required_properties = ["hasMessage", "hasPriority", "hasValidator", "hasTarget"]
        for prop in required_properties:
            prop_uri = self.GUIDANCE[prop]
            if not (prop_uri, RDF.type, OWL.DatatypeProperty) in self.guidance_graph:
                results["errors"].append(f"Missing required property: {prop}")
            
            # Check property domains and ranges
            if not any(self.guidance_graph.triples((prop_uri, RDFS.domain, self.GUIDANCE.ValidationRule))):
                results["errors"].append(f"Missing domain for property: {prop}")
            if not any(self.guidance_graph.triples((prop_uri, RDFS.range, None))):
                results["errors"].append(f"Missing range for property: {prop}")
        
        return results
    
    def validate_shacl_shapes(self) -> Dict[str, List[str]]:
        """Validate the SHACL shapes in the guidance ontology.
        
        Returns:
            Dict mapping validation results to lists of messages
        """
        results: Dict[str, List[str]] = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check that all required SHACL shapes exist
        required_shapes = ["ValidationRuleShape", "ValidationPatternShape"]
        for shape in required_shapes:
            shape_uri = self.GUIDANCE[shape]
            if not (shape_uri, RDF.type, SH.NodeShape) in self.guidance_graph:
                results["errors"].append(f"Missing required SHACL shape: {shape}")
            
            # Check shape properties
            if not any(self.guidance_graph.triples((shape_uri, SH.targetClass, None))):
                results["errors"].append(f"Missing target class for shape: {shape}")
            if not any(self.guidance_graph.triples((shape_uri, SH.property, None))):
                results["errors"].append(f"Missing properties for shape: {shape}")
        
        return results
    
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
        
        # Check ConformanceLevel class exists
        if not (self.GUIDANCE.ConformanceLevel, RDF.type, OWL.Class) in self.guidance_graph:
            results["errors"].append("Missing ConformanceLevel class")
            return results
            
        # Check required conformance levels exist
        required_levels = ["StrictConformance", "ModerateConformance", "BasicConformance"]
        for level in required_levels:
            level_uri = self.GUIDANCE[level]
            if not (level_uri, RDF.type, self.GUIDANCE.ConformanceLevel) in self.guidance_graph:
                results["errors"].append(f"Missing required conformance level: {level}")
            
            # Check label and comment
            if not any(self.guidance_graph.triples((level_uri, RDFS.label, None))):
                results["errors"].append(f"Missing label for conformance level: {level}")
            if not any(self.guidance_graph.triples((level_uri, RDFS.comment, None))):
                results["errors"].append(f"Missing comment for conformance level: {level}")
        
        return results
    
    def validate_integration_process(self) -> Dict[str, List[str]]:
        """Validate the integration process in the guidance ontology.
        
        Returns:
            Dict mapping validation results to lists of messages
        """
        results: Dict[str, List[str]] = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check IntegrationRequirement class exists
        if not (self.GUIDANCE.IntegrationRequirement, RDF.type, OWL.Class) in self.guidance_graph:
            results["errors"].append("Missing IntegrationRequirement class")
            return results
            
        # Check required properties
        required_properties = ["hasIntegrationStep", "hasPrerequisite", "hasOutcome"]
        for prop in required_properties:
            prop_uri = self.GUIDANCE[prop]
            if not (prop_uri, RDF.type, OWL.ObjectProperty) in self.guidance_graph:
                results["errors"].append(f"Missing required integration property: {prop}")
            
            # Check property domains and ranges
            if not any(self.guidance_graph.triples((prop_uri, RDFS.domain, None))):
                results["errors"].append(f"Missing domain for integration property: {prop}")
            if not any(self.guidance_graph.triples((prop_uri, RDFS.range, None))):
                results["errors"].append(f"Missing range for integration property: {prop}")
        
        return results
    
    def validate_test_protocol(self) -> Dict[str, List[str]]:
        """Validate the test protocol in the guidance ontology.
        
        Returns:
            Dict mapping validation results to lists of messages
        """
        results: Dict[str, List[str]] = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Check TestProtocol class exists
        if not (self.GUIDANCE.TestProtocol, RDF.type, OWL.Class) in self.guidance_graph:
            results["errors"].append("Missing TestProtocol class")
            return results
            
        # Check required properties
        required_properties = ["hasTestCase", "hasTestSuite", "hasTestResult"]
        for prop in required_properties:
            prop_uri = self.GUIDANCE[prop]
            if not (prop_uri, RDF.type, OWL.ObjectProperty) in self.guidance_graph:
                results["errors"].append(f"Missing required test protocol property: {prop}")
            
            # Check property domains and ranges
            if not any(self.guidance_graph.triples((prop_uri, RDFS.domain, None))):
                results["errors"].append(f"Missing domain for test protocol property: {prop}")
            if not any(self.guidance_graph.triples((prop_uri, RDFS.range, None))):
                results["errors"].append(f"Missing range for test protocol property: {prop}")
        
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
        rule_results = self.validate_validation_rules()
        shape_results = self.validate_shacl_shapes()
        conformance_results = self.validate_conformance_levels()
        integration_results = self.validate_integration_process()
        test_results = self.validate_test_protocol()
        
        # Combine results
        for key in results:
            results[key].extend(rule_results[key])
            results[key].extend(shape_results[key])
            results[key].extend(conformance_results[key])
            results[key].extend(integration_results[key])
            results[key].extend(test_results[key])
        
        return results

    def validate_against_target(self, target_path: Union[str, Path]) -> Dict[str, List[str]]:
        """Validate the guidance ontology against a target file.
        
        Args:
            target_path: Path to the target file to validate against
            
        Returns:
            Dict mapping validation results to lists of messages
        """
        results: Dict[str, List[str]] = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        # Load target graph
        target_graph = Graph()
        try:
            target_graph.parse(str(target_path), format="turtle")
            results["info"].append(f"Successfully loaded target file: {target_path}")
        except Exception as e:
            results["errors"].append(f"Failed to load target file: {str(e)}")
            return results
            
        # Compare ontology structures
        guidance_classes = set(self.guidance_graph.subjects(RDF.type, OWL.Class))
        target_classes = set(target_graph.subjects(RDF.type, OWL.Class))
        
        # Check for missing classes
        missing_classes = guidance_classes - target_classes
        if missing_classes:
            for cls in missing_classes:
                results["errors"].append(f"Missing required class in target: {cls}")
                
        # Check for extra classes
        extra_classes = target_classes - guidance_classes
        if extra_classes:
            for cls in extra_classes:
                results["warnings"].append(f"Extra class in target not defined in guidance: {cls}")
                
        # Check properties
        guidance_properties = set(self.guidance_graph.subjects(RDF.type, OWL.DatatypeProperty)) | set(self.guidance_graph.subjects(RDF.type, OWL.ObjectProperty))
        target_properties = set(target_graph.subjects(RDF.type, OWL.DatatypeProperty)) | set(target_graph.subjects(RDF.type, OWL.ObjectProperty))
        
        # Check for missing properties
        missing_properties = guidance_properties - target_properties
        if missing_properties:
            for prop in missing_properties:
                results["errors"].append(f"Missing required property in target: {prop}")
                
        # Check for extra properties
        extra_properties = target_properties - guidance_properties
        if extra_properties:
            for prop in extra_properties:
                results["warnings"].append(f"Extra property in target not defined in guidance: {prop}")
                
        # Check SHACL shapes
        guidance_shapes = set(self.guidance_graph.subjects(RDF.type, SH.NodeShape))
        target_shapes = set(target_graph.subjects(RDF.type, SH.NodeShape))
        
        # Check for missing shapes
        missing_shapes = guidance_shapes - target_shapes
        if missing_shapes:
            for shape in missing_shapes:
                results["errors"].append(f"Missing required SHACL shape in target: {shape}")
                
        return results 