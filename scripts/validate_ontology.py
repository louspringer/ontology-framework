#!/usr/bin/env python3
"""Ontology validation script for pre-commit hook."""

import sys
from pathlib import Path
from typing import List, Tuple

import rdflib
from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD

# Import prefix map
from ontology_framework.prefix_map import default_prefix_map

def load_graph(file_path: str) -> Graph:
    """Load an RDF graph from a file.
    
    Args:
        file_path: Path to the ontology file
        
    Returns:
        Loaded RDF graph
    """
    g = Graph()
    
    # Bind all standard prefixes
    default_prefix_map.bind_to_graph(g)
    
    g.parse(file_path, format="turtle")
    return g

def validate_ontology_file(file_path: str) -> Tuple[bool, str]:
    """Validate a single ontology file.
    
    Args:
        file_path: Path to the ontology file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        g = load_graph(file_path)
        
        # Basic validation checks
        validation_errors = []
        
        # Get all prefixes used in the file
        used_prefixes = set()
        for s, p, o in g:
            for node in (s, p, o):
                if isinstance(node, rdflib.URIRef):
                    uri = str(node)
                    for prefix, ns in default_prefix_map.get_all_prefixes().items():
                        if uri.startswith(str(ns)):
                            used_prefixes.add(prefix)
                            break
        
        # Check for required prefixes
        required_prefixes = {"rdf", "rdfs", "owl", "meta", "guidance"}
        for prefix in required_prefixes:
            if prefix not in used_prefixes:
                validation_errors.append(f"Missing required prefix: {prefix}")
        
        # Check for classes having required properties
        for cls in g.subjects(RDF.type, OWL.Class):
            if not any(g.triples((cls, RDFS.label, None))):
                validation_errors.append(f"Class {cls} missing rdfs:label")
            if not any(g.triples((cls, RDFS.comment, None))):
                validation_errors.append(f"Class {cls} missing rdfs:comment")
            if not any(g.triples((cls, OWL.versionInfo, None))):
                validation_errors.append(f"Class {cls} missing owl:versionInfo")
        
        # SHACL validation if shapes graph exists
        shapes_file = Path("guidance/shapes.ttl")
        if shapes_file.exists():
            shapes_graph = load_graph(str(shapes_file))
            conforms, _, results_text = validate(
                g,
                shacl_graph=shapes_graph,
                inference='rdfs',
                abort_on_first=False
            )
            if not conforms:
                validation_errors.append(f"SHACL validation failed:\n{results_text}")
        
        if validation_errors:
            return False, "\n".join(validation_errors)
        return True, "Validation successful"
        
    except Exception as e:
        return False, f"Error validating {file_path}: {str(e)}"

def main(files: List[str]) -> int:
    """Main entry point for the script.
    
    Args:
        files: List of files to validate
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    exit_code = 0
    
    for file_path in files:
        if not file_path.endswith(('.ttl', '.owl', '.rdf')):
            continue
            
        print(f"Validating {file_path}...")
        is_valid, message = validate_ontology_file(file_path)
        
        if not is_valid:
            print(f"Validation failed for {file_path}:")
            print(message)
            exit_code = 1
        else:
            print(f"Validation successful for {file_path}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:])) 