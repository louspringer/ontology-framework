"""Ontology validation functionality for the ontology framework.

This module provides functionality for validating ontologies against various
requirements, including SHACL constraints and custom validation rules.
"""

from typing import Dict, List, Optional, Set, Union, Any
import logging
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from pyshacl import validate
from ontology_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

# Define namespaces
SHACL = Namespace("http://www.w3.org/ns/shacl#")


class OntologyValidator:
    """Validates ontologies against requirements."""

    def __init__(self, ontology_graph: Graph):
        """Initialize ontology validator.

        Args:
            ontology_graph: RDFlib Graph containing the ontology to validate
        """
        self.graph = ontology_graph

    def validate_shacl(self, shapes_graph: Graph) -> Dict[str, Union[bool, List[str]]]:
        """Validate ontology against SHACL shapes.

        Args:
            shapes_graph: RDFlib Graph containing SHACL shapes

        Returns:
            Dictionary with validation results

        Raises:
            ValidationError: If validation fails
        """
        try:
            conforms, results_graph, results_text = validate(
                self.graph, shacl_graph=shapes_graph, inference="rdfs", abort_on_first=False
            )

            return {
                "conforms": conforms,
                "results": results_text.split("\n") if results_text else [],
            }

        except Exception as e:
            raise ValidationError(f"SHACL validation failed: {str(e)}")

    def validate_consistency(self) -> Dict[str, Union[bool, List[str]]]:
        """Validate ontology consistency.

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

        # Check for cycles in class hierarchy
        def get_superclasses(class_uri: URIRef, visited: Set[URIRef]) -> bool:
            if class_uri in visited:
                return True
            visited.add(class_uri)
            for superclass in self.graph.objects(class_uri, RDFS.subClassOf):
                if isinstance(superclass, URIRef):
                    if get_superclasses(superclass, visited):
                        return True
            visited.remove(class_uri)
            return False

        for class_uri in self.graph.subjects(RDF.type, OWL.Class):
            if get_superclasses(class_uri, set()):
                is_valid = False
                issues.append(f"Cycle detected in class hierarchy: {class_uri}")

        return {"is_valid": is_valid, "issues": issues}

    def validate_documentation(self) -> Dict[str, Union[bool, List[str]]]:
        """Validate ontology documentation.

        Returns:
            Dictionary with validation results
        """
        issues = []
        is_valid = True

        # Check for rdfs:label and rdfs:comment
        for subject in self.graph.subjects(RDF.type, OWL.Class):
            if not any(self.graph.triples((subject, RDFS.label, None))):
                is_valid = False
                issues.append(f"Missing rdfs:label for {subject}")
            if not any(self.graph.triples((subject, RDFS.comment, None))):
                is_valid = False
                issues.append(f"Missing rdfs:comment for {subject}")

        # Check for version info
        ontology_uri = self.graph.value(None, RDF.type, OWL.Ontology)
        if ontology_uri:
            if not any(self.graph.triples((ontology_uri, OWL.versionInfo, None))):
                is_valid = False
                issues.append("Missing owl:versionInfo")

        return {"is_valid": is_valid, "issues": issues}

    def validate_naming_conventions(self) -> Dict[str, Union[bool, List[str]]]:
        """Validate ontology naming conventions.

        Returns:
            Dictionary with validation results
        """
        issues = []
        is_valid = True

        # Check class names (should be CamelCase)
        for class_uri in self.graph.subjects(RDF.type, OWL.Class):
            class_name = str(class_uri).split("#")[-1]
            if not class_name[0].isupper() or "_" in class_name:
                is_valid = False
                issues.append(f"Invalid class name (should be CamelCase): {class_name}")

        # Check property names (should be camelCase)
        for prop in self.graph.subjects(RDF.type, OWL.DatatypeProperty):
            prop_name = str(prop).split("#")[-1]
            if prop_name[0].isupper() or "_" in prop_name:
                is_valid = False
                issues.append(f"Invalid property name (should be camelCase): {prop_name}")

        return {"is_valid": is_valid, "issues": issues}


class ValidationManager:
    """Manages validation operations for the ontology framework."""

    def __init__(self):
        """Initialize the validation manager."""
        self.validators = {}
        self._setup_default_validators()

    def _setup_default_validators(self) -> None:
        """Set up default validation rules."""
        self.add_validator("required_fields", self._validate_required_fields)
        self.add_validator("numeric_ranges", self._validate_numeric_ranges)
        self.add_validator("string_format", self._validate_string_format)

    def validate(self, data: Dict[str, Any], rules: List[str]) -> Dict[str, Union[bool, List[str]]]:
        """
        Validate data against specified rules.

        Args:
            data: The data to validate
            rules: List of validation rules to apply

        Returns:
            Dict containing validation result and any issues found
        """
        issues = []
        is_valid = True

        try:
            for rule in rules:
                if rule in self.validators:
                    result = self.validators[rule](data)
                    if not result["is_valid"]:
                        is_valid = False
                        issues.extend(result["issues"])
                else:
                    issues.append(f"Unknown validation rule: {rule}")

            return {"is_valid": is_valid, "issues": issues}
        except Exception as e:
            return {"is_valid": False, "issues": [f"Validation error: {str(e)}"]}

    def _validate_required_fields(self, data: Dict[str, Any]) -> Dict[str, Union[bool, List[str]]]:
        """Validate that all required fields are present."""
        required_fields = ["name", "environment", "port", "replicas"]
        issues = []

        for field in required_fields:
            if field not in data:
                issues.append(f"Missing required field: {field}")

        return {"is_valid": len(issues) == 0, "issues": issues}

    def _validate_numeric_ranges(self, data: Dict[str, Any]) -> Dict[str, Union[bool, List[str]]]:
        """Validate numeric fields are within acceptable ranges."""
        issues = []

        if "port" in data and not (1024 <= data["port"] <= 65535):
            issues.append("Port must be between 1024 and 65535")

        if "replicas" in data and data["replicas"] < 1:
            issues.append("Replicas must be at least 1")

        return {"is_valid": len(issues) == 0, "issues": issues}

    def _validate_string_format(self, data: Dict[str, Any]) -> Dict[str, Union[bool, List[str]]]:
        """Validate string fields match required formats."""
        issues = []

        if "name" in data and not data["name"].isalnum():
            issues.append("Name must contain only alphanumeric characters")

        if "environment" in data and data["environment"] not in ["dev", "staging", "prod"]:
            issues.append("Environment must be one of: dev, staging, prod")

        return {"is_valid": len(issues) == 0, "issues": issues}

    def add_validator(self, name: str, validator: callable) -> None:
        """
        Add a validator function.

        Args:
            name: Name of the validator
            validator: Validator function
        """
        self.validators[name] = validator

    def remove_validator(self, name: str) -> None:
        """
        Remove a validator function.

        Args:
            name: Name of the validator to remove
        """
        if name in self.validators:
            del self.validators[name]
