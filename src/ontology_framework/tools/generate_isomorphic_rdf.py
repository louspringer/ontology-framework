#!/usr/bin/env python3
"""Script to generate isomorphic RDF/XML files from Turtle files."""

import logging
from pathlib import Path
from rdflib import Graph
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_isomorphic_rdf(ttl_file: str) -> bool:
    """Generate an isomorphic RDF/XML file from a Turtle file.
    
    Args:
        ttl_file: Path to the Turtle file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load Turtle file
        g = Graph()
        ttl_path = Path(ttl_file)
        base_iri = f"https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/#{ttl_path.stem}#"
        g.parse(ttl_file, format="turtle", publicID=base_iri)
        
        # Generate RDF/XML file path
        rdf_path = ttl_path.with_suffix('.rdf')
        
        # Save as RDF/XML
        g.serialize(destination=str(rdf_path), format="xml", base=base_iri)
        logger.info(f"Generated isomorphic RDF/XML file: {rdf_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating RDF/XML: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_isomorphic_rdf.py <ttl_file>")
        sys.exit(1)
        
    ttl_file = sys.argv[1]
    if not Path(ttl_file).exists():
        logger.error(f"File not found: {ttl_file}")
        sys.exit(1)
        
    success = generate_isomorphic_rdf(ttl_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 