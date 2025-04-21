#!/usr/bin/env python3

from pathlib import Path
from typing import Dict, List, Set, Optional, Union, Tuple
import logging
import rdflib
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, SH
from rdflib.collection import Collection
from rdflib.term import Node

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define namespaces
TEST = Namespace("http://example.org/test#")
ERROR = Namespace("http://example.org/error#")

def validate_file_path(file_path: str) -> bool:
    """Validate that the file path exists and is a TTL file."""
    path = Path(file_path)
    return path.exists() and path.suffix.lower() == '.ttl'

def create_rdf_list(g: Graph, items: list) -> BNode:
    """Create an RDF list from the given items using RDFlib's Collection."""
    list_node = BNode()
    Collection(g, list_node, items)
    return list_node

def add_error_components(file_path: str) -> None:
    """Add missing error handling components to a TTL file.
    
    Args:
        file_path: Path to the TTL file to process.
        
    Raises:
        ValueError: If the file path is invalid.
        rdflib.plugins.parsers.notation3.BadSyntax: If the TTL file has syntax errors.
    """
    if not validate_file_path(file_path):
        raise ValueError(f"Invalid file path or not a TTL file: {file_path}")
        
    g = Graph()
    try:
        g.parse(file_path, format="turtle")
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {str(e)}")
        raise
    
    # Add base error handling shapes if not present
    error_process = URIRef(ERROR.ErrorProcessShape)
    if (error_process, RDF.type, SH.NodeShape) not in g:
        logger.info(f"Adding ErrorProcessShape to {file_path}")
        g.add((error_process, RDF.type, SH.NodeShape))
        g.add((error_process, RDFS.label, Literal("Error Process Shape")))
        g.add((error_process, RDFS.comment, Literal("Shape for error process tracking")))
        g.add((error_process, SH.targetClass, ERROR.ErrorProcess))
        
        # Add required properties
        properties: List[Tuple[str, str]] = [
            ("code", "Error code identifier"),
            ("message", "Error message description"),
            ("timestamp", "Error occurrence timestamp"),
            ("severity", "Error severity level"),
            ("source", "Error source component")
        ]
        
        for prop, desc in properties:
            prop_shape = URIRef(f"{ERROR}{prop}Shape")
            g.add((error_process, SH.property, prop_shape))
            g.add((prop_shape, SH.path, URIRef(f"{ERROR}{prop}")))
            g.add((prop_shape, SH.minCount, Literal(1)))
            g.add((prop_shape, RDFS.comment, Literal(desc)))

    # Add error type shape if not present
    error_type = ERROR.ErrorType
    if (error_type, RDF.type, SH.NodeShape) not in g:
        logger.info(f"Adding ErrorTypeShape to {file_path}")
        g.add((error_type, RDF.type, SH.NodeShape))
        g.add((error_type, RDFS.label, Literal("Error Type")))
        
        # Add type classification
        type_prop = ERROR.typeShape
        g.add((error_type, SH.property, type_prop))
        g.add((type_prop, SH.path, ERROR.type))
        g.add((type_prop, SH.minCount, Literal(1)))
        
        # Create RDF list for error types using Collection
        error_classes = [
            Literal("SystemError"),
            Literal("UserError"), 
            Literal("ValidationError"),
            Literal("SecurityError")
        ]
        list_node = create_rdf_list(g, error_classes)
        in_prop = URIRef("http://www.w3.org/ns/shacl#in")
        g.add((type_prop, in_prop, list_node))

    # Add error resolution shape if not present
    error_resolution = URIRef(ERROR.ErrorResolutionShape)
    if (error_resolution, RDF.type, SH.NodeShape) not in g:
        logger.info(f"Adding ErrorResolutionShape to {file_path}")
        g.add((error_resolution, RDF.type, SH.NodeShape))
        g.add((error_resolution, RDFS.label, Literal("Error Resolution Shape")))
        g.add((error_resolution, RDFS.comment, Literal("Shape for error resolution tracking")))
        g.add((error_resolution, SH.targetClass, ERROR.ErrorResolution))
        
        # Add resolution properties
        resolution_props: List[Tuple[str, str]] = [
            ("status", "Current resolution status"),
            ("assignee", "Person assigned to resolve"),
            ("resolution_time", "Time taken to resolve"),
            ("action_taken", "Resolution action description")
        ]
        
        for prop, desc in resolution_props:
            prop_shape = URIRef(f"{ERROR}{prop}Shape")
            g.add((error_resolution, SH.property, prop_shape))
            g.add((prop_shape, SH.path, URIRef(f"{ERROR}{prop}")))
            g.add((prop_shape, SH.minCount, Literal(1)))
            g.add((prop_shape, RDFS.comment, Literal(desc)))

    # Add example instances
    process_instance = URIRef(ERROR.ErrorProcess1)
    g.add((process_instance, RDF.type, ERROR.ErrorProcess))
    g.add((process_instance, ERROR.code, Literal("ERR001")))
    g.add((process_instance, ERROR.message, Literal("Example error message")))
    g.add((process_instance, ERROR.timestamp, Literal("2024-03-21T10:00:00Z")))
    g.add((process_instance, ERROR.severity, Literal("HIGH")))
    g.add((process_instance, ERROR.source, Literal("TestComponent")))

    try:
        g.serialize(destination=file_path, format="turtle")
        logger.info(f"Successfully updated {file_path}")
    except Exception as e:
        logger.error(f"Failed to save {file_path}: {str(e)}")
        raise

def find_ttl_files(directory: str) -> List[str]:
    """Find all .ttl files in the specified directory.
    
    Args:
        directory: Directory to search for TTL files.
        
    Returns:
        List of paths to TTL files found.
        
    Raises:
        ValueError: If the directory does not exist.
    """
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Invalid directory path: {directory}")
    
    return [str(p) for p in dir_path.rglob("*.ttl")]

def main() -> None:
    """Main function to process all test files."""
    try:
        test_files = find_ttl_files("tests")
        if not test_files:
            logger.warning("No TTL files found in tests directory")
            return
            
        for file_path in test_files:
            logger.info(f"Processing {file_path}")
            try:
                add_error_components(file_path)
                logger.info(f"Successfully added error handling components to {file_path}")
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 