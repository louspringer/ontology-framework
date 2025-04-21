#!/usr/bin/env python3
"""
Fix prefix issues in Turtle files.
"""

import sys
import logging
import re
from pathlib import Path
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH, DCTERMS, SKOS
from typing import Union, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

def preprocess_content(content: str) -> str:
    """Preprocess the file content to fix common issues."""
    # Remove byte string artifacts
    content = content.replace('b\'', '').replace('\'', '')
    
    # Add default prefix if not present
    if not re.search(r'@prefix\s+:\s+<[^>]+>', content):
        guidance_prefix = '@prefix : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .\n'
        # Find the position after the last @prefix declaration
        prefix_matches = list(re.finditer(r'@prefix[^.]+\.', content))
        if prefix_matches:
            last_prefix = prefix_matches[-1]
            content = content[:last_prefix.end()] + '\n' + guidance_prefix + content[last_prefix.end():]
        else:
            content = guidance_prefix + content
            
    return content

def load_ttl_file(file_path: str) -> Graph:
    """Load a Turtle file into an RDF graph."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Preprocess content
        content = preprocess_content(content)
        
        # Parse the preprocessed content
        graph = Graph()
        graph.parse(data=content, format='turtle')
        return graph
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        raise

def save_ttl_file(graph: Graph, file_path: str) -> None:
    """Save an RDF graph to a Turtle file."""
    try:
        # Always get string output from serialize
        output: str = graph.serialize(format='turtle', encoding='utf-8').decode('utf-8')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(output)
        logger.info(f"Successfully saved {file_path}")
    except Exception as e:
        logger.error(f"Error saving {file_path}: {str(e)}")
        raise

def fix_prefixes(graph: Graph) -> None:
    """Fix prefix issues in the graph."""
    # Remove any numbered prefixes
    for prefix, ns in list(graph.namespaces()):
        if prefix.startswith('sh') and prefix != 'sh':
            # Use bind with empty string to remove prefix
            graph.namespace_manager.bind(prefix, ns, override=True, replace=True)
    
    # Ensure standard prefixes are present
    standard_prefixes = {
        'rdf': RDF,
        'rdfs': RDFS,
        'owl': OWL,
        'xsd': XSD,
        'sh': SH,
        'dcterms': DCTERMS,
        'skos': SKOS,
    }
    
    # Add the guidance namespace as the default prefix if not already present
    GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
    if '' not in [p for p, n in graph.namespaces()]:
        graph.namespace_manager.bind('', GUIDANCE)
    
    for prefix, namespace in standard_prefixes.items():
        if prefix not in [p for p, n in graph.namespaces()]:
            graph.namespace_manager.bind(prefix, namespace)

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python fix_prefixes.py <ttl_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    try:
        # Create backup
        backup_path = file_path + '.bak'
        Path(file_path).rename(backup_path)
        logger.info(f"Created backup at {backup_path}")
        
        # Load the graph
        graph = load_ttl_file(backup_path)
        
        # Fix prefixes
        fix_prefixes(graph)
        
        # Save the changes
        save_ttl_file(graph, file_path)
        
        logger.info("Successfully fixed prefixes")
        
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {str(e)}")
        # Restore from backup if it exists
        if Path(backup_path).exists():
            Path(backup_path).rename(file_path)
            logger.info("Restored from backup")
        sys.exit(1)

if __name__ == '__main__':
    main() 