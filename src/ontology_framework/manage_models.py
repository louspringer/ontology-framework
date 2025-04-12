#!/usr/bin/env python3
"""
Model management module for the ontology framework.
Handles model loading, validation, and integration according to guidance.ttl requirements.
"""

import os
import logging
import traceback
from typing import Dict, List, Optional
from pathlib import Path
import rdflib
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Configure logging with detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Define namespaces
GUIDANCE = Namespace("http://example.org/guidance#")
META = Namespace("http://example.org/meta#")
MODEL = Namespace("http://example.org/model#")

class ModelManager:
    """Manages ontology models according to framework requirements."""
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the model manager.
        
        Args:
            base_dir: Base directory for model files. Defaults to current directory.
        """
        try:
            self.base_dir = Path(base_dir) if base_dir else Path.cwd()
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
                if prefix not in graph.namespaces():
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
            
    def get_model_version(self, model_name: str) -> Optional[str]:
        """
        Get the version of a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Version string if available, None otherwise
        """
        try:
            version = self.versions.get(model_name)
            if version:
                logger.info(f"Retrieved version {version} for model {model_name}")
            else:
                logger.warning(f"No version information found for model {model_name}")
            return version
        except Exception as e:
            logger.error(f"Failed to get version for model {model_name}: {str(e)}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
            
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
        manager = ModelManager(args.base_dir)
        
        if args.load:
            manager.load_model(args.load)
            
        if args.integrate:
            target = args.integrate[0]
            sources = args.integrate[1:]
            manager.integrate_models(target, sources)
            
        if args.save:
            model_name = Path(args.load).stem if args.load else args.integrate[0]
            manager.save_model(model_name, args.save)
            
        if args.version:
            version = manager.get_model_version(args.version)
            if version:
                print(f"Version: {version}")
            else:
                print("No version information available")
                
        if args.dependencies:
            deps = manager.get_model_dependencies(args.dependencies)
            if deps:
                print("Dependencies:")
                for dep in deps:
                    print(f"- {dep}")
            else:
                print("No dependencies found")
                
    except Exception as e:
        logger.error(f"Error in command line interface: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return 1
        
    return 0
    
if __name__ == "__main__":
    exit(main()) 