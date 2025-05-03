#!/usr/bin/env python3
"""Script to validate ontologies in the guidance/modules directory using semantic web tools."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD
import pyshacl
from ontology_framework.tools.guidance_manager import GuidanceManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
SHACL = Namespace("http://www.w3.org/ns/shacl#")

def validate_module(module_path: str, abort_on_error: bool = True) -> Tuple[bool, str]:
    """Validate a single module ontology.
    
    Args:
        module_path: Path to the module ontology file
        abort_on_error: Whether to stop on first error
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Load the module ontology
        module_graph = Graph()
        file_path = Path(module_path)
        
        # Load based on file extension
        if file_path.suffix == '.ttl':
            module_graph.parse(module_path, format="turtle")
        elif file_path.suffix == '.rdf':
            module_graph.parse(module_path, format="xml")
        else:
            return False, f"Unsupported file format: {file_path.suffix}"
            
        # Check for isomorphic counterpart
        counterpart_path = file_path.with_suffix('.ttl' if file_path.suffix == '.rdf' else '.rdf')
        if counterpart_path.exists():
            counterpart_graph = Graph()
            counterpart_graph.parse(str(counterpart_path), format="turtle" if counterpart_path.suffix == '.ttl' else "xml")
            
            # Check if graphs are isomorphic
            if not module_graph.isomorphic(counterpart_graph):
                return False, f"Graphs are not isomorphic: {file_path.name} and {counterpart_path.name}"
        
        # Load SHACL shapes from guidance ontology
        guidance_manager = GuidanceManager()
        shapes_graph = Graph()
        
        # Add core SHACL shapes
        validation_shape = GUIDANCE.ValidationRuleShape
        shapes_graph.add((validation_shape, RDF.type, SHACL.NodeShape))
        shapes_graph.add((validation_shape, SHACL.targetClass, GUIDANCE.ValidationRule))
        
        # Add property shapes
        for prop, datatype in [
            (GUIDANCE.hasMessage, XSD.string),
            (GUIDANCE.hasPriority, XSD.string),
            (GUIDANCE.hasTarget, XSD.anyURI),
            (GUIDANCE.hasValidator, XSD.string)
        ]:
            prop_shape = BNode()
            shapes_graph.add((validation_shape, SHACL.property, prop_shape))
            shapes_graph.add((prop_shape, SHACL.path, prop))
            shapes_graph.add((prop_shape, SHACL.datatype, datatype))
            shapes_graph.add((prop_shape, SHACL.minCount, Literal(1)))
            shapes_graph.add((prop_shape, SHACL.maxCount, Literal(1)))
        
        # Run SHACL validation
        conforms, results_graph, results_text = pyshacl.validate(
            module_graph,
            shacl_graph=shapes_graph,
            ont_graph=None,
            inference='rdfs',
            abort_on_first=abort_on_error,
            allow_warnings=False,
            meta_shacl=False,
            debug=False
        )
        
        if not conforms:
            return False, results_text
            
        # Additional semantic validation using SPARQL
        query = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT ?class ?label ?comment
        WHERE {
            ?class a owl:Class .
            OPTIONAL { ?class rdfs:label ?label }
            OPTIONAL { ?class rdfs:comment ?comment }
        }
        """
        
        results = module_graph.query(query)
        for row in results:
            class_uri = str(row[0])  # Access class URI from first column
            label = str(row[1]) if row[1] else None  # Access label from second column
            comment = str(row[2]) if row[2] else None  # Access comment from third column
            
            if not label or not comment:
                return False, f"Class {class_uri} missing required properties (label or comment)"
        
        return True, "Validation successful"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def validate_all_modules(modules_dir: str = "guidance/modules", abort_on_error: bool = True) -> Dict[str, Tuple[bool, str]]:
    """Validate all ontologies in the modules directory.
    
    Args:
        modules_dir: Path to the modules directory
        abort_on_error: Whether to stop on first error
        
    Returns:
        Dict mapping module paths to validation results
    """
    results = {}
    modules_path = Path(modules_dir)
    
    if not modules_path.exists():
        raise ValueError(f"Modules directory not found: {modules_dir}")
        
    # First validate all Turtle files
    for module_file in modules_path.glob("**/*.ttl"):
        logger.info(f"Validating {module_file}")
        is_valid, message = validate_module(str(module_file), abort_on_error)
        results[str(module_file)] = (is_valid, message)
        
        if not is_valid and abort_on_error:
            logger.error(f"Validation failed for {module_file}: {message}")
            break
            
    # Then validate all RDF/XML files
    for module_file in modules_path.glob("**/*.rdf"):
        logger.info(f"Validating {module_file}")
        is_valid, message = validate_module(str(module_file), abort_on_error)
        results[str(module_file)] = (is_valid, message)
        
        if not is_valid and abort_on_error:
            logger.error(f"Validation failed for {module_file}: {message}")
            break
            
    return results

if __name__ == "__main__":
    results = validate_all_modules(abort_on_error=True)
    
    # Print results
    for module_path, (is_valid, message) in results.items():
        if is_valid:
            logger.info(f"{module_path}: Validation successful")
        else:
            logger.error(f"{module_path}: Validation failed - {message}")
            
    # Exit with error if any validation failed
    if not all(is_valid for is_valid, _ in results.values()):
        exit(1) 