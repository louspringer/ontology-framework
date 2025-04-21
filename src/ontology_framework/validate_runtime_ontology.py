"""Validation script for runtime error handling ontology.

This script validates the runtime error handling ontology using RDFlib
and checks for compliance with SHACL shapes and other requirements.
"""

from pathlib import Path
from typing import List, Optional, NoReturn
import logging
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL
import sys

# Define SHACL namespace
SHACL = Namespace("http://www.w3.org/ns/shacl#")

logger = logging.getLogger(__name__)

class RuntimeOntologyValidator:
    """Validates the runtime error handling ontology."""
    
    def __init__(self, ontology_file: Path):
        """Initialize the validator.
        
        Args:
            ontology_file: Path to the ontology TTL file
        """
        self.ontology_file = ontology_file
        self.graph = Graph()
        self.ns = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/#")
        
    def load_ontology(self) -> None:
        """Load the ontology file into RDFlib graph.
        
        Raises:
            Exception: If ontology file cannot be loaded
        """
        try:
            self.graph.parse(self.ontology_file, format="turtle")
            logger.info(f"Loaded ontology from {self.ontology_file}")
        except Exception as e:
            logger.error(f"Failed to load ontology: {str(e)}")
            raise
            
    def validate_classes(self) -> List[str]:
        """Validate required classes are present with labels and comments.
        
        Returns:
            List of validation issues
        """
        issues = []
        required_classes = [
            "ErrorType",
            "ErrorHandlingStep", 
            "ErrorHandlingProcess",
            "TestErrorHandlingProcess"
        ]
        
        for class_name in required_classes:
            class_uri = self.ns[class_name]
            if (class_uri, RDF.type, OWL.Class) not in self.graph:
                issues.append(f"Missing required class: {class_name}")
                continue
                
            if not any(self.graph.triples((class_uri, RDFS.label, None))):
                issues.append(f"Missing rdfs:label for class: {class_name}")
                
            if not any(self.graph.triples((class_uri, RDFS.comment, None))):
                issues.append(f"Missing rdfs:comment for class: {class_name}")
                
        return issues
        
    def validate_properties(self) -> List[str]:
        """Validate required properties with domains and ranges.
        
        Returns:
            List of validation issues
        """
        issues = []
        required_properties = [
            ("hasStepOrder", OWL.DatatypeProperty),
            ("hasStepAction", OWL.DatatypeProperty),
            ("hasProcessStep", OWL.ObjectProperty)
        ]
        
        for prop_name, prop_type in required_properties:
            prop_uri = self.ns[prop_name]
            if (prop_uri, RDF.type, prop_type) not in self.graph:
                issues.append(f"Missing required property: {prop_name}")
                continue
                
            if not any(self.graph.triples((prop_uri, RDFS.domain, None))):
                issues.append(f"Missing rdfs:domain for property: {prop_name}")
                
            if not any(self.graph.triples((prop_uri, RDFS.range, None))):
                issues.append(f"Missing rdfs:range for property: {prop_name}")
                
        return issues
        
    def validate_instances(self) -> List[str]:
        """Validate required instances and their properties.
        
        Returns:
            List of validation issues
        """
        issues = []
        required_instances = [
            ("ErrorIdentification", "ErrorHandlingStep"),
            ("ErrorAnalysis", "ErrorHandlingStep"),
            ("ErrorRecovery", "ErrorHandlingStep"),
            ("ErrorPrevention", "ErrorHandlingStep"),
            ("standardErrorHandling", "ErrorHandlingProcess")
        ]
        
        for instance_name, class_name in required_instances:
            instance_uri = self.ns[instance_name]
            class_uri = self.ns[class_name]
            
            if (instance_uri, RDF.type, class_uri) not in self.graph:
                issues.append(f"Missing required instance: {instance_name} of type {class_name}")
                
        return issues
        
    def validate_shacl_shapes(self) -> List[str]:
        """Validate SHACL shapes and constraints.
        
        Returns:
            List of validation issues
        """
        issues = []
        required_shapes = [
            "ErrorHandlingProcessShape",
            "TestErrorHandlingProcessShape"
        ]
        
        for shape_name in required_shapes:
            shape_uri = self.ns[shape_name]
            if (shape_uri, RDF.type, SHACL.NodeShape) not in self.graph:
                issues.append(f"Missing required SHACL shape: {shape_name}")
                continue
                
            # Validate shape has target class
            if not any(self.graph.triples((shape_uri, SHACL.targetClass, None))):
                issues.append(f"Missing sh:targetClass for shape: {shape_name}")
                
            # Validate shape has properties
            if not any(self.graph.triples((shape_uri, SHACL.property, None))):
                issues.append(f"Missing sh:property for shape: {shape_name}")
                
        return issues
        
    def validate_all(self) -> List[str]:
        """Run all validation checks.
        
        Returns:
            List of all validation issues
        """
        try:
            self.load_ontology()
            
            all_issues = []
            all_issues.extend(self.validate_classes())
            all_issues.extend(self.validate_properties())
            all_issues.extend(self.validate_instances())
            all_issues.extend(self.validate_shacl_shapes())
            
            return all_issues
            
        except Exception as e:
            return [f"Validation failed with error: {str(e)}"]

def main() -> NoReturn:
    """Main entry point for validation script."""
    logging.basicConfig(level=logging.INFO)
    
    ontology_file = Path("guidance/modules/runtime_error_handling.ttl")
    if not ontology_file.exists():
        logger.error(f"Ontology file not found: {ontology_file}")
        sys.exit(1)
        
    validator = RuntimeOntologyValidator(ontology_file)
    issues = validator.validate_all()
    
    if issues:
        logger.error("Validation failed with the following issues:")
        for issue in issues:
            logger.error(f"- {issue}")
        sys.exit(1)
    else:
        logger.info("Validation successful - no issues found")
        sys.exit(0)

if __name__ == "__main__":
    main() 