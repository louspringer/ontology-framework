"""SPORE validation functionality for the ontology framework.

This module provides functionality for validating ontologies against SPORE
(Semantic Patterns for Ontology Reuse and Evolution) patterns.
"""

from typing import Dict, List, Optional, Set, Tuple
import logging
import traceback
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL
from .exceptions import ValidationError

# Define the guidance namespace
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add file handler if not already present
if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
    fh = logging.FileHandler('spore_validation.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

class SporeValidator:
    """Validator for SPORE patterns."""

    def __init__(self, ontology_graph: Optional[Graph] = None):
        """Initialize the validator.
        
        Args:
            ontology_graph: Optional RDF graph to validate against
        """
        self.graph = ontology_graph or Graph()
        logger.info("Initialized SporeValidator with graph containing %d triples", len(self.graph))

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
            logger.info("Starting SPORE validation for %s with target model %s", spore_uri, target_model)
            messages = []
            is_valid = True
            
            # Check if spore exists and has correct type
            logger.debug("Checking SPORE existence and type")
            spore_types = list(self.graph.objects(spore_uri, RDF.type))
            if not spore_types:
                msg = f"SPORE {spore_uri} not found in graph"
                logger.error(msg)
                messages.append(msg)
                return False, messages
                
            logger.debug("Found SPORE types: %s", spore_types)
            if GUIDANCE.Spore not in spore_types:
                msg = f"Invalid SPORE type: {spore_types}"
                logger.error(msg)
                messages.append(msg)
                return False, messages

            # Validate patches
            patches = list(self.graph.objects(spore_uri, GUIDANCE.distributesPatch))
            if not patches:
                msg = f"No patches found for SPORE {spore_uri}"
                logger.error(msg)
                messages.append(msg)
                return False, messages

            # Validate each patch
            for patch in patches:
                if not self._validate_patch(patch, target_model):
                    msg = f"Invalid patch: {patch}"
                    logger.error(msg)
                    messages.append(msg)
                    is_valid = False
                    
            return is_valid, messages
            
        except Exception as e:
            logger.error("SPORE validation failed: %s", str(e))
            logger.error("Traceback: %s", traceback.format_exc())
            raise ValidationError(f"SPORE validation failed: {str(e)}")

    def _validate_patch(self, patch_uri: URIRef, target_model: URIRef) -> bool:
        """Validate a concept patch.
        
        Args:
            patch_uri: URI of the patch to validate
            target_model: URI of the target model
            
        Returns:
            bool: True if patch is valid
        """
        try:
            logger.debug("Validating patch %s for target model %s", patch_uri, target_model)
            
            # Check patch type
            patch_types = list(self.graph.objects(patch_uri, RDF.type))
            if GUIDANCE.ConceptPatch not in patch_types:
                logger.error("Invalid patch type: %s", patch_types)
                return False

            # Check target model
            target_models = list(self.graph.objects(patch_uri, GUIDANCE.modifiesModel))
            if not target_models or target_model not in target_models:
                logger.error("Invalid target model for patch %s: %s", patch_uri, target_models)
                return False

            # Check target concept
            target_concepts = list(self.graph.objects(patch_uri, GUIDANCE.appliesTo))
            if not target_concepts:
                logger.error("No target concept found for patch %s", patch_uri)
                return False

            return True

        except Exception as e:
            logger.error("Patch validation failed: %s", str(e))
            logger.error("Traceback: %s", traceback.format_exc())
            return False

    def validate_patch(self, patch_uri: URIRef) -> Tuple[bool, List[str]]:
        """Validate a single patch.
        
        Args:
            patch_uri: URI of the patch to validate
            
        Returns:
            Tuple of (is_valid, list of validation messages)
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            logger.info(f"Starting patch validation for {patch_uri}")
            messages = []
            is_valid = True
            
            # Check patch type
            patch_types = list(self.graph.objects(patch_uri, RDF.type))
            if not patch_types:
                msg = f"Patch {patch_uri} not found in graph"
                logger.error(msg)
                messages.append(msg)
                return False, messages
                
            if GUIDANCE.ConceptPatch not in patch_types:
                msg = f"Invalid patch type: {patch_types}"
                logger.error(msg)
                messages.append(msg)
                return False, messages
                
            # Check required properties
            required_properties = [
                GUIDANCE.appliesTo,
                GUIDANCE.modifiesModel,
                OWL.versionInfo,
                RDFS.label,
                RDFS.comment
            ]
            
            for prop in required_properties:
                if not any(self.graph.triples((patch_uri, prop, None))):
                    msg = f"Missing required property: {prop}"
                    logger.error(msg)
                    messages.append(msg)
                    is_valid = False
                    
            logger.info(f"Patch validation completed. Valid: {is_valid}")
            return is_valid, messages
            
        except Exception as e:
            logger.error(f"Patch validation failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ValidationError(f"Patch validation failed: {str(e)}")
            
    def validate_model_compatibility(self, spore_uri: URIRef, target_model: URIRef) -> Tuple[bool, List[str]]:
        """Validate compatibility between a SPORE and target model.
        
        Args:
            spore_uri: URI of the SPORE to validate
            target_model: URI of the target model
            
        Returns:
            Tuple of (is_valid, list of validation messages)
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            logger.info(f"Starting model compatibility validation for SPORE {spore_uri} and model {target_model}")
            messages = []
            is_valid = True
            
            # Check model exists
            if not any(self.graph.triples((target_model, None, None))):
                msg = f"Target model {target_model} not found in graph"
                logger.error(msg)
                messages.append(msg)
                return False, messages
                
            # Check model version compatibility
            model_version = next(self.graph.objects(target_model, OWL.versionInfo), None)
            spore_version = next(self.graph.objects(spore_uri, OWL.versionInfo), None)
            
            if not model_version or not spore_version:
                msg = "Missing version information"
                logger.error(msg)
                messages.append(msg)
                return False, messages
                
            # Compare versions (implement version comparison logic here)
            if str(model_version) < str(spore_version):
                msg = f"Model version {model_version} is older than SPORE version {spore_version}"
                logger.error(msg)
                messages.append(msg)
                is_valid = False
                
            logger.info(f"Model compatibility validation completed. Valid: {is_valid}")
            return is_valid, messages
            
        except Exception as e:
            logger.error(f"Model compatibility validation failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ValidationError(f"Model compatibility validation failed: {str(e)}")
            
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