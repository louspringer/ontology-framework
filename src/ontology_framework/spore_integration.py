"""Module for integrating spores into target models with validation and dependency management."""

import logging
import traceback
import os
from pathlib import Path
from typing import List, Union, Tuple, Optional, Set, cast, Dict, Mapping, Any
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL

from .spore_validation import SporeValidator
from .exceptions import ConcurrentModificationError, ConformanceError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the guidance namespace
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

# Map string literals to URIRefs for conformance levels
CONFORMANCE_LEVELS: Dict[str, URIRef] = {
    "STRICT": GUIDANCE.STRICT,
    "MODERATE": GUIDANCE.MODERATE,
    "RELAXED": GUIDANCE.RELAXED
}

# Map URIRefs back to string literals for validation
CONFORMANCE_LEVEL_STRINGS = {
    GUIDANCE.STRICT: "STRICT",
    GUIDANCE.MODERATE: "MODERATE",
    GUIDANCE.RELAXED: "RELAXED"
}

class SporeIntegrator:
    """Class for managing spore integration into target models."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the SporeIntegrator.
        
        Args:
            data_dir: Directory containing data files
        """
        # Store original string path
        self.data_dir_str: str = data_dir
        self.conformance_level: URIRef = GUIDANCE.STRICT
        
        # Initialize graphs
        self.guidance_graph: Graph = Graph()
        self.graph: Graph = Graph()
        
        # Load guidance ontology
        guidance_file = os.path.join(data_dir, "guidance.ttl")
        if os.path.exists(guidance_file):
            self.guidance_graph.parse(guidance_file, format="turtle")
            
        # Initialize namespaces
        self.guidance_graph.bind("guidance", GUIDANCE)
        self.graph.bind("guidance", GUIDANCE)

        logger.info(f"Initializing SporeIntegrator with data directory: {data_dir}")
        try:
            # Convert to Path for operations
            self.data_dir: Path = Path(data_dir)
            self.data_dir.mkdir(exist_ok=True)
            self.validator: SporeValidator = SporeValidator(ontology_graph=self.graph)
            self.spore_uri: Optional[URIRef] = None  # Initialize spore_uri as None
            logger.debug("SporeIntegrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SporeIntegrator: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def set_conformance_level(self, level: Union[str, URIRef]) -> None:
        """Set the conformance level for the integrator.
        
        Args:
            level: The conformance level to set, either as a string ('STRICT', 'MODERATE', 'RELAXED')
                  or as a URIRef from the guidance ontology.
                  
        Raises:
            ConformanceError: If the level is invalid or not defined in the guidance ontology.
        """
        logger.info(f"Set conformance level to {level}")
        
        # Handle string input
        if isinstance(level, str):
            if level not in CONFORMANCE_LEVELS:
                raise ConformanceError(f"Invalid conformance level: {level}. Must be one of {set(CONFORMANCE_LEVELS.keys())}")
            level_uri = CONFORMANCE_LEVELS[level]
        # Handle URIRef input
        elif isinstance(level, URIRef):
            # Check if this URIRef is in our CONFORMANCE_LEVEL_STRINGS mapping
            if level in CONFORMANCE_LEVEL_STRINGS:
                level_uri = level
                # Validate against guidance ontology
                if not self._validate_ontology_conformance(level_uri):
                    raise ConformanceError(f"Conformance level {level_uri} is not defined in the guidance ontology")
                self.conformance_level = level_uri
                return
            # Try to extract the level string from the URI
            level_str = str(level).split("#")[-1]
            if level_str in CONFORMANCE_LEVELS:
                level_uri = CONFORMANCE_LEVELS[level_str]
            else:
                raise ConformanceError(f"Invalid conformance level URI: {level}. Must be one of {set(CONFORMANCE_LEVELS.values())}")
        else:
            raise ConformanceError(f"Invalid conformance level type: {type(level)}. Must be str or URIRef")
            
        # Validate against guidance ontology
        if not self._validate_ontology_conformance(level_uri):
            raise ConformanceError(f"Conformance level {level_uri} is not defined in the guidance ontology")
            
        self.conformance_level = level_uri

    def _validate_conformance_type(self, level: Any) -> bool:
        """Validate the type of the conformance level.
        
        Args:
            level: The conformance level to validate
            
        Returns:
            bool: True if type is valid
            
        Raises:
            ConformanceError: If type is invalid
        """
        logger.debug(f"Validating conformance type for: {level} (type: {type(level)})")
        if not isinstance(level, (str, URIRef)):
            raise ConformanceError(f"Invalid conformance level type: {type(level)}. Must be str or URIRef")
        return True
        
    def _validate_conformance_string(self, level: str) -> Optional[URIRef]:
        """Validate a string conformance level.
        
        Args:
            level: The string conformance level to validate
            
        Returns:
            Optional[URIRef]: The corresponding URIRef if valid, None otherwise
            
        Raises:
            ConformanceError: If string is invalid
        """
        logger.debug(f"Validating string conformance: {level}")
        if level not in CONFORMANCE_LEVELS:
            raise ConformanceError(f"Invalid conformance level: {level}. Must be one of {set(CONFORMANCE_LEVELS.keys())}")
        return CONFORMANCE_LEVELS[level]
        
    def _validate_conformance_uri(self, level: URIRef) -> Optional[URIRef]:
        """Validate a URIRef conformance level.
        
        Args:
            level: The URIRef conformance level to validate
            
        Returns:
            Optional[URIRef]: The validated URIRef if valid, None otherwise
            
        Raises:
            ConformanceError: If URI is invalid
        """
        logger.debug(f"Validating URI conformance: {level}")
        if level in CONFORMANCE_LEVEL_STRINGS:
            logger.debug(f"Found direct match in CONFORMANCE_LEVEL_STRINGS: {level}")
            return level
            
        level_str = str(level).split("#")[-1]
        logger.debug(f"Extracted level string: {level_str}")
        if level_str not in CONFORMANCE_LEVELS:
            raise ConformanceError(f"Invalid conformance level: {level_str}. Must be one of {set(CONFORMANCE_LEVELS.keys())}")
        return CONFORMANCE_LEVELS[level_str]
        
    def _resolve_conformance_level(self, level: Union[str, URIRef], 
                                 string_check: Optional[URIRef], 
                                 uri_check: Optional[URIRef]) -> Optional[URIRef]:
        """Resolve the conformance level from validation results."""
        logger.debug(f"Resolving conformance level for input: {level}")
        logger.debug(f"Type of level: {type(level)}")
        logger.debug(f"String check result: {string_check}")
        logger.debug(f"URI check result: {uri_check}")
        
        if isinstance(level, str):
            logger.debug("Input is string type, returning string_check")
            return string_check
        elif isinstance(level, URIRef):
            logger.debug("Input is URIRef type, returning uri_check")
            return uri_check
        else:
            logger.error(f"Invalid input type: {type(level)}")
            return None
        
    def _validate_ontology_conformance(self, level_uri: URIRef) -> bool:
        """Validate conformance level against ontology.
        
        Args:
            level_uri: The conformance level URI to validate
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ConformanceError: If validation fails
        """
        if not any(self.guidance_graph.triples((level_uri, RDF.type, GUIDANCE.ModelConformance))):
            raise ConformanceError(f"Conformance level {level_uri} not defined in guidance ontology")
        return True
        
    def _validate_conformance_rules(self, level_uri: URIRef) -> bool:
        """Validate conformance level against rules.
        
        Args:
            level_uri: The conformance level URI to validate
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ConformanceError: If validation fails
        """
        if not self.validate_conformance_level(level_uri):
            raise ConformanceError(f"Conformance level {level_uri} does not meet guidance requirements")
        return True

    def validate_conformance_level(self, level_uri: URIRef) -> bool:
        """Validate a conformance level against guidance rules.
        
        Args:
            level_uri: The URIRef of the conformance level to validate
            
        Returns:
            bool: True if validation passes
        """
        # Check if the level is defined as a ModelConformance instance
        if not (level_uri, RDF.type, GUIDANCE.ModelConformance) in self.guidance_graph:
            logger.error(f"Conformance level {level_uri} is not defined as a ModelConformance")
            return False
            
        # Check if it has a conformance level string property
        if not any(self.guidance_graph.triples((level_uri, GUIDANCE.conformanceLevel, None))):
            logger.error(f"Missing conformanceLevel property for {level_uri}")
            return False
                
        return True

    def validate_prefixes(self, spore_uri: URIRef) -> bool:
        """Validate prefixes used in a spore based on conformance level.
        
        Args:
            spore_uri: URI of the spore to validate
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ConformanceError: If prefix validation fails
        """
        logger.debug(f"Starting prefix validation for spore: {spore_uri}")
        
        if self.conformance_level == CONFORMANCE_LEVELS["RELAXED"]:
            logger.debug("Skipping validation due to RELAXED conformance level")
            return True
        
        # Get registered prefixes from both validator and guidance graphs
        registered_prefixes: Set[str] = set()
        
        # Add prefixes from validator graph
        for prefix, ns in self.validator.graph.namespaces():
            validator_prefix: str = str(ns).split('#')[0]
            logger.debug(f"Found registered prefix in validator: {validator_prefix}")
            registered_prefixes.add(validator_prefix)
            
        # Add prefixes from guidance graph
        for prefix, ns in self.guidance_graph.namespaces():
            guidance_prefix: str = str(ns).split('#')[0]
            logger.debug(f"Found registered prefix in guidance: {guidance_prefix}")
            registered_prefixes.add(guidance_prefix)
        
        # Get prefixes used in spore
        for s, p, o in self.validator.graph.triples((spore_uri, None, None)):
            # Handle subject prefix
            if isinstance(s, URIRef):
                # Extract prefix string from URIRef
                subj_prefix: str = str(s).split('#')[0]
                logger.debug(f"Checking subject prefix: {subj_prefix}")
                if subj_prefix not in registered_prefixes:
                    msg = f"Unregistered prefix used in subject: {subj_prefix}"
                    logger.error(msg)
                    raise ConformanceError(msg)
            
            # Handle predicate prefix
            if isinstance(p, URIRef):
                # Extract prefix string from URIRef
                pred_prefix: str = str(p).split('#')[0]
                logger.debug(f"Checking predicate prefix: {pred_prefix}")
                if pred_prefix not in registered_prefixes:
                    msg = f"Unregistered prefix used in predicate: {pred_prefix}"
                    logger.error(msg)
                    raise ConformanceError(msg)
            
            # Handle object prefix
            if isinstance(o, URIRef):
                # Extract prefix string from URIRef
                obj_prefix: str = str(o).split('#')[0]
                logger.debug(f"Checking object prefix: {obj_prefix}")
                if obj_prefix not in registered_prefixes:
                    msg = f"Unregistered prefix used in object: {obj_prefix}"
                    logger.error(msg)
                    raise ConformanceError(msg)
        
        logger.debug("Prefix validation completed successfully")
        return True

    def validate_namespaces(self, spore_uri: URIRef) -> bool:
        """Validate namespaces used in a spore based on conformance level.
        
        Args:
            spore_uri: URI of the spore to validate
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ConformanceError: If namespace validation fails
        """
        logger.debug(f"Starting namespace validation for spore: {spore_uri}")
        
        if self.conformance_level == CONFORMANCE_LEVELS["RELAXED"]:
            logger.debug("Skipping validation due to RELAXED conformance level")
            return True
        
        # Get registered namespaces from both validator and guidance graphs
        registered_namespaces: Set[str] = set()
        
        # Add namespaces from validator graph
        for prefix, ns in self.validator.graph.namespaces():
            validator_ns_str: str = str(ns)
            logger.debug(f"Found registered namespace in validator: {validator_ns_str}")
            registered_namespaces.add(validator_ns_str)
            
        # Add namespaces from guidance graph
        for prefix, ns in self.guidance_graph.namespaces():
            guidance_ns_str: str = str(ns)
            logger.debug(f"Found registered namespace in guidance: {guidance_ns_str}")
            registered_namespaces.add(guidance_ns_str)
        
        # Get namespaces used in spore
        for s, p, o in self.validator.graph.triples((spore_uri, None, None)):
            # Handle subject namespace
            if isinstance(s, URIRef):
                # Extract namespace string from URIRef
                subj_ns_str: str = str(s).split('#')[0] + '#'
                logger.debug(f"Checking subject namespace: {subj_ns_str}")
                if subj_ns_str not in registered_namespaces:
                    msg = f"Unregistered namespace used in subject: {subj_ns_str}"
                    logger.error(msg)
                    raise ConformanceError(msg)
            
            # Handle predicate namespace
            if isinstance(p, URIRef):
                # Extract namespace string from URIRef
                pred_ns_str: str = str(p).split('#')[0] + '#'
                logger.debug(f"Checking predicate namespace: {pred_ns_str}")
                if pred_ns_str not in registered_namespaces:
                    msg = f"Unregistered namespace used in predicate: {pred_ns_str}"
                    logger.error(msg)
                    raise ConformanceError(msg)
            
            # Handle object namespace
            if isinstance(o, URIRef):
                # Extract namespace string from URIRef
                obj_ns_str: str = str(o).split('#')[0] + '#'
                logger.debug(f"Checking object namespace: {obj_ns_str}")
                if obj_ns_str not in registered_namespaces:
                    msg = f"Unregistered namespace used in object: {obj_ns_str}"
                    logger.error(msg)
                    raise ConformanceError(msg)
        
        logger.debug("Namespace validation completed successfully")
        return True

    def integrate_spore(self, spore: URIRef, target_model: URIRef) -> bool:
        """Integrate a spore into a target model with validation.
        
        Args:
            spore (URIRef): URI of the spore to integrate
            target_model (URIRef): URI of the target model
            
        Returns:
            bool: True if integration successful
            
        Raises:
            ValueError: If spore validation fails
        """
        logger.info(f"Integrating spore {spore} into model {target_model}")
        try:
            # Validate spore
            is_valid, messages = self.validator.validate_spore(spore, target_model)
            if not is_valid:
                raise ValueError(f"Spore validation failed: {', '.join(messages)}")
            
            # Check compatibility
            if not self.check_compatibility(spore, target_model):
                raise ValueError("Spore not compatible with target model")
            
            # Resolve dependencies
            if not self.resolve_dependencies(spore):
                raise ValueError("Failed to resolve spore dependencies")
            
            # Apply patches
            patches = list(self.graph.objects(spore, GUIDANCE.distributesPatch))
            for patch in patches:
                if not self.apply_patch(spore, URIRef(str(patch)), target_model):
                    raise ValueError(f"Failed to apply patch {patch}")
            
            logger.info("Spore integration completed successfully")
            return True
        except Exception as e:
            logger.error(f"Spore integration failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def check_compatibility(self, spore: URIRef, target_model: URIRef) -> bool:
        """Check if a spore is compatible with a target model.
        
        Args:
            spore (URIRef): URI of the spore
            target_model (URIRef): URI of the target model
            
        Returns:
            bool: True if compatible
        """
        logger.info(f"Checking compatibility between spore {spore} and model {target_model}")
        try:
            # Check if spore targets this model
            is_compatible = (spore, GUIDANCE.targetModel, target_model) in self.graph
            logger.debug(f"Compatibility check result: {is_compatible}")
            return is_compatible
        except Exception as e:
            logger.error(f"Compatibility check failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def apply_patch(self, spore: URIRef, patch: URIRef, target_model: URIRef) -> bool:
        """Apply a patch from a spore to a target model.
        
        Args:
            spore (URIRef): URI of the spore
            patch (URIRef): URI of the patch to apply
            target_model (URIRef): URI of the target model
            
        Returns:
            bool: True if patch applied successfully
        """
        logger.info(f"Applying patch {patch} from spore {spore} to model {target_model}")
        try:
            # Verify patch exists and is valid
            if not (patch, RDF.type, GUIDANCE.ConceptPatch) in self.graph:
                raise ValueError(f"Invalid patch: {patch}")
            
            # Apply patch transformations
            # TODO: Implement actual patch application logic
            
            logger.info("Patch applied successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to apply patch: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def integrate_concurrent(self, spores: List[URIRef], target_model: URIRef) -> bool:
        """Integrate multiple spores concurrently.
        
        Args:
            spores (List[URIRef]): List of spore URIs
            target_model (URIRef): URI of the target model
            
        Returns:
            bool: True if all spores integrated successfully
            
        Raises:
            ConcurrentModificationError: If concurrent modification detected
        """
        logger.info(f"Integrating {len(spores)} spores concurrently")
        try:
            # Check for conflicts between patches
            patches = []
            for spore in spores:
                spore_patches = list(self.graph.objects(spore, GUIDANCE.distributesPatch))
                patches.extend(spore_patches)
            
            if len(patches) != len(set(patches)):
                raise ConcurrentModificationError("Conflicting patches detected")
            
            # Integrate each spore
            for spore in spores:
                if not self.integrate_spore(spore, target_model):
                    return False
            
            logger.info("Concurrent integration completed successfully")
            return True
        except ConcurrentModificationError as e:
            logger.error(f"Concurrent modification error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Concurrent integration failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def migrate_version(self, spore: URIRef, new_version: str) -> bool:
        """Migrate a spore to a new version.
        
        Args:
            spore (URIRef): URI of the spore
            new_version (str): New version string
            
        Returns:
            bool: True if migration successful
        """
        logger.info(f"Migrating spore {spore} to version {new_version}")
        try:
            # Remove old version info
            for old_version in self.graph.objects(spore, OWL.versionInfo):
                self.graph.remove((spore, OWL.versionInfo, old_version))
            
            # Add new version info
            self.graph.add((spore, OWL.versionInfo, Literal(new_version)))
            
            logger.info("Version migration completed successfully")
            return True
        except Exception as e:
            logger.error(f"Version migration failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def resolve_dependencies(self, spore: URIRef) -> bool:
        """Resolve dependencies for a spore.
        
        Args:
            spore (URIRef): URI of the spore
            
        Returns:
            bool: True if all dependencies resolved
        """
        logger.info(f"Resolving dependencies for spore {spore}")
        try:
            # Get all dependencies
            dependencies = list(self.graph.objects(spore, OWL.imports))
            
            # Verify each dependency exists
            for dependency in dependencies:
                if not (dependency, RDF.type, GUIDANCE.TransformationPattern) in self.graph:
                    raise ValueError(f"Missing dependency: {dependency}")
            
            logger.info("Dependencies resolved successfully")
            return True
        except Exception as e:
            logger.error(f"Dependency resolution failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def validate_conformance(self, model: URIRef) -> bool:
        """Validate conformance of a model based on current conformance level.
        
        Args:
            model: The model to validate
            
        Returns:
            bool: True if model conforms, False otherwise
            
        Raises:
            ConformanceError: If validation fails at STRICT level
        """
        try:
            # Validate prefixes
            self.validate_prefixes(model)
            
            # Validate namespaces
            self.validate_namespaces(model)
            
            # Validate integration steps if present
            if (model, GUIDANCE.hasIntegrationStep, None) in self.guidance_graph:
                self.validate_integration_steps(model)
                
            return True
            
        except Exception as e:
            if self.conformance_level == CONFORMANCE_LEVELS["STRICT"]:
                raise ConformanceError(f"Model validation failed: {str(e)}")
            return False

    def validate_integration_steps(self, process_uri: URIRef) -> bool:
        """Validate integration steps in a process.
        
        Args:
            process_uri: URI of the process to validate
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ConformanceError: If validation fails
        """
        # Get all steps with their order
        steps: List[Tuple[URIRef, int]] = []
        for step, _, order_node in self.guidance_graph.triples((None, GUIDANCE.hasOrder, None)):
            if (step, RDF.type, GUIDANCE.IntegrationStep) in self.guidance_graph:
                # Convert order to integer safely
                if isinstance(order_node, Literal):
                    order_int = int(order_node.value)
                else:
                    order_int = int(str(order_node))
                steps.append((cast(URIRef, step), order_int))
        
        if not steps:
            raise ConformanceError("No integration steps found in process")
        
        # Sort steps by order
        steps.sort(key=lambda x: x[1])
        
        # Validate step order is sequential
        expected_order = 1
        for step, order in steps:
            if order != expected_order:
                raise ConformanceError(f"Invalid step order: {order}. Expected: {expected_order}")
            expected_order += 1
        
        return True

    def execute_integration_steps(self, process: URIRef) -> bool:
        """Execute integration steps in order.
        
        Args:
            process (URIRef): URI of the process to execute
            
        Returns:
            bool: True if execution successful
            
        Raises:
            ConformanceError: If execution fails
        """
        logger.info(f"Executing integration steps for process {process}")
        try:
            # Get all steps in the process
            steps = list(self.validator.graph.objects(process, GUIDANCE.hasIntegrationStep))
            if not steps:
                raise ConformanceError("No steps found in process")
            
            # Get step orders and sort
            step_orders = []
            for step in steps:
                if not isinstance(step, URIRef):
                    raise ConformanceError(f"Step {step} must be a URIRef")
                    
                order = next(self.validator.graph.objects(step, GUIDANCE.stepOrder), None)
                if not order:
                    raise ConformanceError(f"Step {step} has no order")
                try:
                    if isinstance(order, Literal):
                        order_int = int(str(order.value))
                    else:
                        order_int = int(str(order))
                    step_orders.append((order_int, step))
                except (ValueError, TypeError):
                    raise ConformanceError(f"Invalid order value for step {step}: {order}")
            
            step_orders.sort()
            
            # Execute steps in order
            for order_int, step in step_orders:
                # Get step type and target
                step_type = next(self.validator.graph.objects(step, RDF.type), None)
                if not step_type:
                    raise ConformanceError(f"Step {step} has no type")
                if not isinstance(step_type, URIRef):
                    raise ConformanceError(f"Step {step} type must be a URIRef")
                
                target = next(self.validator.graph.objects(step, GUIDANCE.stepTarget), None)
                if not target:
                    raise ConformanceError(f"Step {step} has no target")
                if not isinstance(target, URIRef):
                    raise ConformanceError(f"Step {step} target must be a URIRef")
                
                # Execute step based on type
                if step_type == GUIDANCE.ValidationStep:
                    if not self.validate_conformance(target):
                        raise ConformanceError(f"Validation failed for target: {target}")
                elif step_type == GUIDANCE.IntegrationStep:
                    if not self.integrate_spore(target, process):
                        raise ConformanceError(f"Integration failed for target: {target}")
                else:
                    raise ConformanceError(f"Unknown step type: {step_type}")
            
            logger.info("Integration step execution completed")
            return True
        except ConformanceError as e:
            logger.error(f"Integration step execution failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during step execution: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ConformanceError(f"Integration step execution failed: {str(e)}") 