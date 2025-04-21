#!/usr/bin/env python3
"""
Edit TTL files by fixing prefix issues.
"""

import sys
import logging
import re
import shutil
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, SH, XSD
from rdflib.plugins.parsers.notation3 import BadSyntax
from typing import Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

def clean_content(content: str) -> str:
    """Clean the content by removing byte string artifacts and fixing common issues."""
    # Remove byte string artifacts
    content = content.replace('b\'', '').replace('\'', '')
    
    # Fix numbered prefixes
    prefix_map = {
        'rdf1:': 'rdf:',
        'rdfs1:': 'rdfs:',
        'owl1:': 'owl:',
        'sh1:': 'sh:',
        'xsd1:': 'xsd:'
    }
    
    for old, new in prefix_map.items():
        content = content.replace(old, new)
    
    # Fix common syntax issues
    content = re.sub(r',\s*\.', ',', content)  # Remove period after comma
    content = re.sub(r'\s*,\s*]', ']', content)  # Remove comma before closing bracket
    
    return content

def fix_file(file_path: str) -> str:
    """Fix a TTL file by parsing and reserializing it. Returns the fixed content."""
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        raise ValueError("Input file is empty")
    
    # Clean the content
    content = clean_content(content)
    
    # Add default prefix if not present
    if not '@prefix : <' in content:
        content = '@prefix : <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .\n\n' + content
    
    # Parse into a graph
    g = Graph()
    try:
        g.parse(data=content, format='turtle')
        logger.info("Successfully parsed file")
    except Exception as e:
        logger.error(f"Error parsing file: {str(e)}")
        # Try to parse line by line to identify the problematic line
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip():  # Only try to parse non-empty lines
                try:
                    g.parse(data=line, format='turtle')
                except Exception as line_error:
                    logger.error(f"Error at line {i}: {line}")
                    logger.error(f"Line error: {str(line_error)}")
        raise
    
    # Add standard prefixes
    standard_prefixes = {
        'rdf': RDF,
        'rdfs': RDFS,
        'owl': OWL,
        'xsd': XSD,
        'sh': SH
    }
    
    for prefix, namespace in standard_prefixes.items():
        g.bind(prefix, namespace)
    
    # Add default prefix
    GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
    g.bind('', GUIDANCE)
    
    # Serialize to string
    serialized: Union[str, bytes] = g.serialize(format='turtle')
    if isinstance(serialized, bytes):
        return serialized.decode('utf-8')
    return serialized

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python edit_ttl.py <ttl_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    # Create backup
    backup_path = file_path + '.bak'
    temp_path = file_path + '.tmp'
    
    try:
        # Create backup
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup at {backup_path}")
        
        # Fix the file content
        fixed_content = fix_file(backup_path)
        
        # Write the fixed content to a temporary file first
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # If successful, replace the original file
        shutil.move(temp_path, file_path)
        logger.info("Successfully updated file")
        
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {str(e)}")
        # Restore from backup
        if Path(backup_path).exists():
            shutil.copy2(backup_path, file_path)
            logger.info("Restored from backup")
        if Path(temp_path).exists():
            Path(temp_path).unlink()
        sys.exit(1)
    finally:
        # Clean up temporary files
        if Path(backup_path).exists():
            Path(backup_path).unlink()
        if Path(temp_path).exists():
            Path(temp_path).unlink()

if __name__ == "__main__":
    main() 