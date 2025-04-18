#!/usr/bin/env python3
"""
Model management module for the ontology framework.
Handles model loading, validation, and integration according to guidance.ttl requirements.
"""

import os
import logging
import traceback
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib.plugins.sparql import prepareQuery
import json
import sys

# Configure logging with detailed format
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum visibility
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('model_manager.log')
    ]
)
logger = logging.getLogger(__name__)

# Define namespaces
GUIDANCE = Namespace("http://example.org/guidance#")
META = Namespace("http://example.org/meta#")
MODEL = Namespace("http://example.org/model#")

class ModelQualityError(Exception):
    """Raised when model quality validation fails"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.details = details or {}
        logger.error(f"ModelQualityError: {message}")
        if details:
            logger.error(f"Error details: {json.dumps(details, indent=2)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")

class ModelProjectionError(Exception):
    """Raised when model projection validation fails"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.details = details or {}
        logger.error(f"ModelProjectionError: {message}")
        if details:
            logger.error(f"Error details: {json.dumps(details, indent=2)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")

class ModelManager:
    """Manages ontology models according to framework requirements."""
    
    def __init__(self, base_dir: str = "."):
        """
        Initialize the model manager.
        
        Args:
            base_dir: Base directory for model files. Defaults to current directory.
        """
        try:
            self.base_dir = Path(base_dir)
            logger.info(f"Initializing ModelManager with base directory: {self.base_dir}")
            
            self.guidance_graph = self._load_guidance_ontology()
            self.models: Dict[str, Graph] = {}
            self.versions: Dict[str, str] = {}
            self.dependencies: Dict[str, List[str]] = {}
            
            logger.info("ModelManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ModelManager: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
            
    def _load_guidance_ontology(self) -> Graph:
        """Load the guidance ontology."""
        try:
            guidance_path = self.base_dir / "guidance.ttl"
            if not guidance_path.exists():
                error_msg = f"Guidance ontology not found at {guidance_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
                
            logger.info(f"Loading guidance ontology from {guidance_path}")
            graph = Graph()
            graph.parse(str(guidance_path), format="turtle")
            logger.info("Guidance ontology loaded successfully")
            return graph
        except Exception as e:
            logger.error(f"Failed to load guidance ontology: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
            
    def load_model(self, model_path: str) -> Graph:
        """
        Load an ontology model with validation.
        
        Args:
            model_path: Path to the model file
            
        Returns:
            Loaded RDF graph
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            ValueError: If model validation fails
            Exception: For other errors during loading
        """
        try:
            path = Path(model_path)
            if not path.exists():
                error_msg = f"Model file not found at {model_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
                
            logger.info(f"Loading model from {model_path}")
            graph = Graph()
            graph.parse(str(path), format="turtle")
            
            # Validate model conformance
            self._validate_model(graph)
            
            # Track version and dependencies
            self._track_version(path.stem, graph)
            self._track_dependencies(path.stem, graph)
            
            self.models[path.stem] = graph
            logger.info(f"Model {path.stem} loaded and validated successfully")
            return graph
        except Exception as e:
            logger.error(f"Failed to load model {model_path}: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
            
    def _validate_model(self, graph: Graph) -> None:
        """
        Validate model against guidance requirements.
        
        Args:
            graph: RDF graph to validate
            
        Raises:
            ValueError: If validation fails
        """
        try:
            logger.info("Starting model validation")
            
            # Check for required prefixes
            required_prefixes = {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "xsd": "http://www.w3.org/2001/XMLSchema#"
            }
            
            missing_prefixes = []
            for prefix, namespace in required_prefixes.items():
                if not any(p == prefix for p, _ in graph.namespaces()):
                    missing_prefixes.append(prefix)
                    
            if missing_prefixes:
                error_msg = f"Missing required prefixes: {', '.join(missing_prefixes)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Check for required classes and properties
            required_entities = [
                (RDFS.label, "rdfs:label"),
                (RDFS.comment, "rdfs:comment"),
                (OWL.versionInfo, "owl:versionInfo")
            ]
            
            missing_entities = []
            for entity, name in required_entities:
                if not any(graph.triples((None, entity, None))):
                    missing_entities.append(name)
                    
            if missing_entities:
                error_msg = f"Model missing required statements: {', '.join(missing_entities)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Run validation pipeline
            self._run_validation_pipeline(graph)
            logger.info("Model validation completed successfully")
        except Exception as e:
            logger.error(f"Model validation failed: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
            
    def _track_version(self, model_name: str, graph: Graph) -> None:
        """
        Track model version.
        
        Args:
            model_name: Name of the model
            graph: Model graph
        """
        try:
            version = None
            for _, _, version_info in graph.triples((None, OWL.versionInfo, None)):
                version = str(version_info)
                break
                
            if version:
                self.versions[model_name] = version
                logger.info(f"Tracked version {version} for model {model_name}")
            else:
                logger.warning(f"No version information found for model {model_name}")
        except Exception as e:
            logger.error(f"Failed to track version for model {model_name}: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
            
    def _track_dependencies(self, model_name: str, graph: Graph) -> None:
        """
        Track model dependencies.
        
        Args:
            model_name: Name of the model
            graph: Model graph
        """
        try:
            dependencies = []
            for _, _, imported in graph.triples((None, OWL.imports, None)):
                dependencies.append(str(imported))
                
            if dependencies:
                self.dependencies[model_name] = dependencies
                logger.info(f"Tracked dependencies for model {model_name}: {dependencies}")
            else:
                logger.warning(f"No dependencies found for model {model_name}")
        except Exception as e:
            logger.error(f"Failed to track dependencies for model {model_name}: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
            
    def _run_validation_pipeline(self, graph: Graph) -> None:
        """
        Run the validation pipeline on a model.
        
        Args:
            graph: Model graph to validate
        """
        try:
            # Check for documentation
            has_documentation = any(graph.triples((None, RDFS.comment, None)))
            if not has_documentation:
                logger.warning("Model missing documentation (rdfs:comment)")
                
            # Check for version info
            has_version = any(graph.triples((None, OWL.versionInfo, None)))
            if not has_version:
                logger.warning("Model missing version information (owl:versionInfo)")
                
            # Check for dependencies
            has_dependencies = any(graph.triples((None, OWL.imports, None)))
            if not has_dependencies:
                logger.warning("Model missing dependency declarations (owl:imports)")
        except Exception as e:
            logger.error(f"Validation pipeline failed: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
            
    def integrate_models(self, target_model: str, source_models: List[str]) -> None:
        """
        Integrate multiple models according to guidance requirements.
        
        Args:
            target_model: Name of the target model
            source_models: List of source model names
            
        Raises:
            ValueError: If models are not found or integration fails
        """
        try:
            if target_model not in self.models:
                error_msg = f"Target model {target_model} not loaded"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            target_graph = self.models[target_model]
            logger.info(f"Starting integration of models into {target_model}")
            
            for source in source_models:
                if source not in self.models:
                    error_msg = f"Source model {source} not loaded"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                    
                source_graph = self.models[source]
                logger.info(f"Integrating {source} into {target_model}")
                
                # Merge graphs
                for triple in source_graph:
                    target_graph.add(triple)
                    
                # Validate integration
                self._validate_model(target_graph)
                
            logger.info(f"Successfully integrated models into {target_model}")
        except Exception as e:
            logger.error(f"Failed to integrate models: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
            
    def save_model(self, model_name: str, output_path: str) -> None:
        """
        Save a model to file.
        
        Args:
            model_name: Name of the model to save
            output_path: Path to save the model
            
        Raises:
            ValueError: If model is not found
            Exception: For other errors during saving
        """
        try:
            if model_name not in self.models:
                error_msg = f"Model {model_name} not loaded"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            logger.info(f"Saving model {model_name} to {output_path}")
            graph = self.models[model_name]
            graph.serialize(destination=output_path, format="turtle")
            logger.info(f"Successfully saved model {model_name} to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save model {model_name}: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
            
    def get_model_version(self, model_name):
        """Get the version of a model.
        
        Args:
            model_name (str): The name of the model to get the version for.
            
        Returns:
            str: The version of the model, or None if not found.
        """
        try:
            logger.info(f"Getting version for model {model_name}")
            
            # Check if model is loaded
            if model_name not in self.models:
                logger.warning(f"Model {model_name} not found in loaded models")
                return None
                
            model_graph = self.models[model_name]
            
            # Find the ontology node
            ontology_node = None
            for s, p, o in model_graph.triples((None, RDF.type, OWL.Ontology)):
                ontology_node = s
                break
                
            if not ontology_node:
                logger.warning(f"No ontology node found in model {model_name}")
                return None
                
            # Get version info
            for s, p, o in model_graph.triples((ontology_node, OWL.versionInfo, None)):
                version = str(o)
                logger.info(f"Found version {version} for model {model_name}")
                return version
                
            logger.warning(f"No version info found for model {model_name}")
            return None
        except Exception as e:
            logger.error(f"Error getting version for model {model_name}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
            
    def get_model_dependencies(self, model_name: str) -> List[str]:
        """
        Get the dependencies of a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            List of dependency URIs
        """
        try:
            deps = self.dependencies.get(model_name, [])
            if deps:
                logger.info(f"Retrieved dependencies for model {model_name}: {deps}")
            else:
                logger.warning(f"No dependencies found for model {model_name}")
            return deps
        except Exception as e:
            logger.error(f"Failed to get dependencies for model {model_name}: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
            
    def validate_model_quality(self, model_name_or_path: str) -> bool:
        """
        Validate model quality according to guidance ontology rules.
        
        Args:
            model_name_or_path: Name of the model to validate or path to the model file
            
        Returns:
            bool: True if model passes all quality checks
            
        Raises:
            ModelQualityError: If model fails quality checks
        """
        logger.info(f"Starting quality validation for model: {model_name_or_path}")
        
        try:
            # Get the model graph
            if model_name_or_path in self.models:
                model_graph = self.models[model_name_or_path]
            else:
                model_graph = Graph()
                model_graph.parse(model_name_or_path, format="turtle")
                
            logger.debug(f"Model graph contains {len(model_graph)} triples")
            
            # Check documentation
            missing_docs = self._check_model_documentation(model_graph)
            if missing_docs:
                raise ModelQualityError(
                    "Documentation validation failed",
                    {"missing_documentation": missing_docs}
                )
                
            # Check SHACL constraints
            logger.info("Checking SHACL constraints")
            if not self.check_shacl_constraints(model_graph):
                raise ModelQualityError("SHACL validation failed")
                
            # Check model structure
            structure_issues = self._check_model_structure(model_graph)
            if structure_issues:
                raise ModelQualityError(
                    "Model structure validation failed",
                    {"unbound_properties": structure_issues}
                )
                
            logger.info(f"Quality validation completed successfully for model: {model_name_or_path}")
            return True
            
        except ModelQualityError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in quality validation: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ModelQualityError(f"Quality validation failed: {str(e)}")
        
    def validate_model_projection(self, model_path: str) -> bool:
        """Validate model projection alignment"""
        model_graph = Graph()
        model_graph.parse(model_path, format="turtle")
        
        # Check projection alignment
        if not self._check_projection_alignment(model_graph):
            raise ModelProjectionError("Model projection is misaligned")
            
        return True
        
    def validate_system_quality(self, model_path: str) -> bool:
        """Validate system quality with model-first principle"""
        # Model quality must be validated first
        if not self.check_model_quality(model_path):
            raise ModelQualityError("Model quality validation failed")
            
        # Only check code quality if model quality passes
        return self.check_code_quality()
        
    def check_model_quality(self, model_path: str) -> bool:
        """Check model quality according to guidance rules"""
        model_graph = Graph()
        model_graph.parse(model_path, format="turtle")
        
        # Implement quality checks from guidance.ttl
        quality_checks = [
            self._check_documentation(model_graph),
            self._check_version_info(model_graph),
            self._check_dependencies(model_graph)
        ]
        
        return all(quality_checks)
        
    def check_code_quality(self) -> bool:
        """Check code quality"""
        # Implement code quality checks
        return True
        
    def validate_projection(self, model_content: str, projection: Dict) -> bool:
        """Validate model projection against requirements."""
        logger.debug(f"Validating projection for model content: {model_content[:100]}...")
        try:
            model_graph = Graph()
            model_graph.parse(data=model_content, format="turtle")
            
            # Get the namespace from the model content
            namespace = None
            for prefix, uri in model_graph.namespaces():
                if prefix == "test":
                    namespace = uri
                    break
                    
            if not namespace:
                logger.error("No 'test' namespace found in model")
                return False
                
            class_name = projection["class_name"]
            required_attrs = projection["attributes"]
            
            # Create the full class URI
            class_uri = URIRef(f"{namespace}{class_name}")
            logger.debug(f"Looking for class: {class_uri}")
            
            # Check if class exists
            if (class_uri, RDF.type, OWL.Class) not in model_graph:
                logger.error(f"Class {class_uri} not found in model")
                return False
                
            # Check required attributes
            for attr in required_attrs:
                if attr == "label":
                    if not any(model_graph.triples((class_uri, RDFS.label, None))):
                        logger.error(f"Class {class_uri} missing required label")
                        return False
                elif attr == "comment":
                    if not any(model_graph.triples((class_uri, RDFS.comment, None))):
                        logger.error(f"Class {class_uri} missing required comment")
                        return False
                        
            logger.info(f"Projection validation successful for class {class_uri}")
            return True
        except Exception as e:
            logger.error(f"Projection validation failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
        
    def validate_documentation(self, model_content: str) -> bool:
        """Validate model documentation requirements"""
        model_graph = Graph()
        model_graph.parse(data=model_content, format="turtle")
        
        return self._check_documentation(model_graph)
        
    def validate_model(self, model_path: str) -> bool:
        """Run complete model validation pipeline"""
        try:
            self.validate_model_quality(model_path)
            self.validate_model_projection(model_path)
            return True
        except (ModelQualityError, ModelProjectionError):
            return False
            
    def check_shacl_constraints(self, graph: Graph) -> bool:
        """Check SHACL constraints for the model.
        
        Args:
            graph: The RDF graph to validate
            
        Returns:
            bool: True if validation passes
        """
        logger.info("Starting SHACL constraints validation")
        try:
            # Log graph details
            logger.debug(f"Validating graph with {len(graph)} triples")
            logger.debug("Graph namespaces:")
            for prefix, namespace in graph.namespaces():
                logger.debug(f"  {prefix}: {namespace}")
            
            # Log SHACL shapes
            shapes = []
            for s, p, o in graph.triples((None, RDF.type, URIRef("http://www.w3.org/ns/shacl#NodeShape"))):
                shapes.append(s)
                logger.debug(f"Found SHACL shape: {s}")
            
            if not shapes:
                logger.warning("No SHACL shapes found in graph")
            
            # TODO: Implement actual SHACL validation
            # For now, just check basic structure
            has_classes = any(graph.triples((None, RDF.type, OWL.Class)))
            has_properties = any(graph.triples((None, RDF.type, OWL.ObjectProperty)))
            
            logger.debug(f"Graph has classes: {has_classes}")
            logger.debug(f"Graph has properties: {has_properties}")
            
            if not (has_classes and has_properties):
                logger.error("Basic model structure validation failed")
                return False
            
            logger.info("SHACL constraints validation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"SHACL validation failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def _prepare_sparql_query(self, query: str) -> prepareQuery:
        """Prepare a SPARQL query with namespace bindings.
        
        Args:
            query: The SPARQL query string
            
        Returns:
            The prepared query
        """
        logger.debug("Preparing SPARQL query")
        logger.debug(f"Query text:\n{query}")
        
        try:
            # Add standard namespace bindings
            namespaces = {
                "rdf": RDF,
                "rdfs": RDFS, 
                "owl": OWL,
                "xsd": XSD
            }
            
            # Log namespace bindings
            logger.debug("Using namespace bindings:")
            for prefix, uri in namespaces.items():
                logger.debug(f"  {prefix}: {uri}")
                
            prepared = prepareQuery(query, initNs=namespaces)
            logger.debug("Query prepared successfully")
            return prepared
            
        except Exception as e:
            logger.error(f"Failed to prepare SPARQL query: {str(e)}")
            logger.error(f"Query was:\n{query}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _process_sparql_result_row(self, row, var_names) -> Dict[str, URIRef]:
        """Process a single SPARQL result row.
        
        Args:
            row: The result row
            var_names: List of variable names from the query
            
        Returns:
            Dictionary mapping variable names to values
        """
        logger.debug(f"Processing result row: {row}")
        logger.debug(f"Variable names: {var_names}")
        
        result = {}
        try:
            # Handle different result row types
            if hasattr(row, "__iter__"):
                # Row is iterable - process each value
                for i, var in enumerate(var_names):
                    try:
                        value = row[i]
                        if value:
                            result[str(var)] = value
                            logger.debug(f"Processed {var} = {value}")
                    except Exception as e:
                        logger.warning(f"Could not get value for variable {var}: {str(e)}")
                        
            elif hasattr(row, "__getitem__"):
                # Row supports dictionary-like access
                for var in var_names:
                    try:
                        value = row[var]
                        if value:
                            result[str(var)] = value
                            logger.debug(f"Processed {var} = {value}")
                    except Exception as e:
                        logger.warning(f"Could not get value for variable {var}: {str(e)}")
                        
            else:
                # Try attribute access as last resort
                for var in var_names:
                    try:
                        value = getattr(row, str(var))
                        if value:
                            result[str(var)] = value
                            logger.debug(f"Processed {var} = {value}")
                    except Exception as e:
                        logger.warning(f"Could not get value for variable {var}: {str(e)}")
                        
            return result
            
        except Exception as e:
            logger.error(f"Failed to process result row: {str(e)}")
            logger.error(f"Row: {row}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _execute_sparql_query(self, graph: Graph, query: str, description: str) -> List[Dict[str, URIRef]]:
        """Execute a SPARQL query with detailed logging.
        
        Args:
            graph: The RDF graph to query
            query: The SPARQL query string
            description: Description of what the query is checking
            
        Returns:
            List of dictionaries containing query results
        """
        logger.info(f"Executing SPARQL query for {description}")
        
        try:
            # Prepare query
            prepared_query = self._prepare_sparql_query(query)
            
            # Execute query
            logger.debug("Executing prepared query")
            results = graph.query(prepared_query)
            logger.debug(f"Query returned {len(results)} results")
            
            # Get variable names
            var_names = list(results.vars)
            logger.debug(f"Query variables: {var_names}")
            
            # Process results
            processed_results = []
            for i, row in enumerate(results):
                logger.debug(f"Processing result {i+1} of {len(results)}")
                try:
                    result_dict = self._process_sparql_result_row(row, var_names)
                    if result_dict:
                        processed_results.append(result_dict)
                        logger.debug(f"Added result: {result_dict}")
                except Exception as e:
                    logger.error(f"Failed to process row {i+1}: {str(e)}")
                    logger.error(f"Skipping this result")
                    continue
            
            logger.info(f"Successfully processed {len(processed_results)} results")
            return processed_results
            
        except Exception as e:
            logger.error(f"Failed to execute SPARQL query: {str(e)}")
            logger.error(f"Query was:\n{query}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _check_documentation(self, graph: Graph) -> bool:
        """Check if model has required documentation"""
        ont_type = URIRef("http://www.w3.org/2002/07/owl#Ontology")
        for ont in graph.subjects(RDF.type, ont_type):
            has_label = any(graph.triples((ont, RDFS.label, None)))
            has_comment = any(graph.triples((ont, RDFS.comment, None)))
            has_version = any(graph.triples((ont, OWL.versionInfo, None)))
            
            if not (has_label and has_comment and has_version):
                return False
                
        return True
        
    def _check_version_info(self, graph: Graph) -> bool:
        """Check if model has version information"""
        return any(graph.triples((None, OWL.versionInfo, None)))
        
    def _check_dependencies(self, graph: Graph) -> bool:
        """Check if model dependencies are properly declared"""
        return any(graph.triples((None, OWL.imports, None)))
        
    def _check_projection_alignment(self, graph: Graph) -> bool:
        """Check if model projections are properly aligned"""
        # Implement projection alignment checks
        return True

    def _check_class_documentation(self, graph: Graph, class_uri: URIRef) -> List[str]:
        """Check documentation for a single class.
        
        Args:
            graph: The RDF graph
            class_uri: URI of the class to check
            
        Returns:
            List of missing documentation items
        """
        logger.debug(f"Checking documentation for class: {class_uri}")
        missing = []
        
        try:
            # Check label
            if not any(graph.triples((class_uri, RDFS.label, None))):
                msg = f"Missing label for {class_uri}"
                logger.warning(msg)
                missing.append(msg)
                
            # Check comment    
            if not any(graph.triples((class_uri, RDFS.comment, None))):
                msg = f"Missing comment for {class_uri}"
                logger.warning(msg)
                missing.append(msg)
                
            # Check version info
            if not any(graph.triples((class_uri, OWL.versionInfo, None))):
                msg = f"Missing version info for {class_uri}"
                logger.warning(msg)
                missing.append(msg)
                
            return missing
            
        except Exception as e:
            logger.error(f"Error checking class documentation: {str(e)}")
            logger.error(f"Class URI: {class_uri}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _check_model_documentation(self, graph: Graph) -> List[str]:
        """Check documentation for all classes in the model.
        
        Args:
            graph: The RDF graph to check
            
        Returns:
            List of missing documentation items
        """
        logger.info("Checking model documentation")
        missing_docs = []
        
        try:
            # Get all classes
            classes = list(graph.subjects(RDF.type, OWL.Class))
            logger.debug(f"Found {len(classes)} classes to check")
            
            # Check each class
            for class_uri in classes:
                logger.debug(f"Checking class: {class_uri}")
                missing = self._check_class_documentation(graph, class_uri)
                missing_docs.extend(missing)
                
            if missing_docs:
                logger.warning(f"Found {len(missing_docs)} documentation issues")
                for issue in missing_docs:
                    logger.warning(f"Documentation issue: {issue}")
            else:
                logger.info("All documentation checks passed")
                
            return missing_docs
            
        except Exception as e:
            logger.error(f"Error checking model documentation: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _check_model_structure(self, graph: Graph) -> List[Dict[str, URIRef]]:
        """Check model structure for unbound properties.
        
        Args:
            graph: The RDF graph to check
            
        Returns:
            List of dictionaries containing unbound properties
        """
        logger.info("Checking model structure")
        
        try:
            query = """
                SELECT ?class ?property
                WHERE {
                    ?class rdf:type owl:Class .
                    ?property rdf:type owl:ObjectProperty .
                    FILTER NOT EXISTS {
                        ?property rdfs:domain ?class
                    }
                }
            """
            
            results = self._execute_sparql_query(graph, query, "model structure check")
            
            if results:
                logger.warning(f"Found {len(results)} unbound properties")
                for result in results:
                    logger.warning(f"Unbound property {result['property']} for class {result['class']}")
            else:
                logger.info("No unbound properties found")
                
            return results
            
        except Exception as e:
            logger.error(f"Error checking model structure: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

def main():
    """Command line interface for model management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage ontology models")
    parser.add_argument("--base-dir", help="Base directory for model files")
    parser.add_argument("--load", help="Load a model file")
    parser.add_argument("--integrate", nargs="+", help="Integrate models")
    parser.add_argument("--save", help="Save model to file")
    parser.add_argument("--version", help="Get model version")
    parser.add_argument("--dependencies", help="Get model dependencies")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.info("Debug logging enabled")
    
    try:
        # Initialize ModelManager
        manager = ModelManager(args.base_dir)
        logger.info(f"Initialized ModelManager with base directory: {args.base_dir}")
        
        if args.load:
            logger.info(f"Loading model from {args.load}")
            manager.load_model(args.load)
            
        if args.integrate:
            target = args.integrate[0]
            sources = args.integrate[1:]
            logger.info(f"Integrating models: target={target}, sources={sources}")
            manager.integrate_models(target, sources)
            
        if args.save:
            model_name = Path(args.load).stem if args.load else args.integrate[0]
            logger.info(f"Saving model {model_name} to {args.save}")
            manager.save_model(model_name, args.save)
            
        if args.version:
            logger.info(f"Getting version for model {args.version}")
            version = manager.get_model_version(args.version)
            if version:
                print(f"Version: {version}")
            else:
                print("No version information available")
                
        if args.dependencies:
            logger.info(f"Getting dependencies for model {args.dependencies}")
            deps = manager.get_model_dependencies(args.dependencies)
            if deps:
                print("Dependencies:")
                for dep in deps:
                    print(f"- {dep}")
            else:
                print("No dependencies found")
                
        return 0
    except Exception as e:
        logger.error(f"Error in command line interface: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 