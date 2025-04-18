#!/usr/bin/env python3
"""Validation module for ontology framework."""

import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, OWL
from rdflib.plugins.parsers.notation3 import BadSyntax
from urllib.parse import urlparse

class ValidationError(Exception):
    """Base exception for validation errors."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

class OntologyValidator:
    """Validator for ontology files and operations."""
    
    def __init__(self):
        """Initialize validator."""
        self.logger = logging.getLogger(__name__)
        
    def validate_turtle_syntax(self, file_path: Union[str, Path]) -> List[str]:
        """Validate Turtle syntax of a file.
        
        Args:
            file_path: Path to Turtle file
            
        Returns:
            List of validation errors
            
        Raises:
            ValidationError: If file cannot be read
        """
        errors = []
        try:
            self.logger.info(f"Validating Turtle syntax for {file_path}")
            g = Graph()
            g.parse(file_path, format="turtle")
            self.logger.debug(f"Successfully parsed {file_path}")
        except BadSyntax as e:
            error_msg = f"Turtle syntax error in {file_path}: {str(e)}"
            self.logger.error(error_msg)
            errors.append(error_msg)
        except Exception as e:
            error_msg = f"Failed to parse file {file_path}: {e}"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)
        return errors
        
    def validate_context_uri(self, uri: str) -> List[str]:
        """Validate a context URI.
        
        Args:
            uri: Context URI to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        try:
            self.logger.info(f"Validating context URI: {uri}")
            parsed = urlparse(uri)
            
            if not parsed.scheme:
                error_msg = f"URI {uri} must have a scheme (e.g., http://)"
                self.logger.error(error_msg)
                errors.append(error_msg)
                
            if parsed.scheme == "file":
                error_msg = f"File URIs are not allowed for contexts: {uri}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                
            if not parsed.netloc and parsed.scheme != "urn":
                error_msg = f"URI {uri} must have a netloc (host) or be a URN"
                self.logger.error(error_msg)
                errors.append(error_msg)
                
            if not errors:
                self.logger.debug(f"Context URI {uri} is valid")
                
        except Exception as e:
            error_msg = f"Invalid URI format for {uri}: {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
        return errors
        
    def validate_ontology_structure(self, file_path: Union[str, Path]) -> List[str]:
        """Validate ontology structure.
        
        Args:
            file_path: Path to ontology file
            
        Returns:
            List of validation errors
        """
        errors = []
        try:
            self.logger.info(f"Validating ontology structure for {file_path}")
            g = Graph()
            g.parse(file_path, format="turtle")
            
            # Check for required ontology metadata
            ontologies = list(g.subjects(RDF.type, OWL.Ontology))
            if not ontologies:
                error_msg = f"No owl:Ontology declaration found in {file_path}"
                self.logger.error(error_msg)
                errors.append(error_msg)
            else:
                self.logger.debug(f"Found {len(ontologies)} ontology declarations in {file_path}")
                
            # Check for proper class definitions
            classes = list(g.subjects(RDF.type, OWL.Class))
            self.logger.debug(f"Found {len(classes)} classes in {file_path}")
            
            for cls in classes:
                if not (cls, RDFS.label, None) in g:
                    error_msg = f"Class {cls} missing rdfs:label in {file_path}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
                if not (cls, RDFS.comment, None) in g:
                    error_msg = f"Class {cls} missing rdfs:comment in {file_path}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
                    
            if not errors:
                self.logger.info(f"Ontology structure validation passed for {file_path}")
                
        except Exception as e:
            error_msg = f"Failed to validate structure of {file_path}: {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
        return errors
        
    def validate_before_import(self, 
                             file_path: Union[str, Path],
                             context_uri: Optional[str] = None) -> List[str]:
        """Run all validations before import.
        
        Args:
            file_path: Path to ontology file
            context_uri: Optional context URI to validate
            
        Returns:
            List of all validation errors
        """
        self.logger.info(f"Starting pre-import validation for {file_path}")
        errors = []
        
        # Validate Turtle syntax
        syntax_errors = self.validate_turtle_syntax(file_path)
        errors.extend(syntax_errors)
        
        # Validate context URI if provided
        if context_uri:
            uri_errors = self.validate_context_uri(context_uri)
            errors.extend(uri_errors)
            
        # Validate ontology structure
        structure_errors = self.validate_ontology_structure(file_path)
        errors.extend(structure_errors)
        
        if errors:
            self.logger.error(f"Validation failed for {file_path} with {len(errors)} errors")
        else:
            self.logger.info(f"All validations passed for {file_path}")
            
        return errors 