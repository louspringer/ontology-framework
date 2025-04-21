#!/usr/bin/env python3
"""
RDF Editor - A tool for editing and managing Turtle (TTL) files.
"""

import sys
import logging
import re
import shutil
from pathlib import Path
from typing import Union, Optional, Dict, List, Any
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH, DCTERMS, SKOS
from rdflib.term import Node

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

class RDFEditor:
    """Class for editing and managing RDF/Turtle files."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.graph = Graph()
        self.backup_path = file_path + '.bak'
        self.temp_path = file_path + '.tmp'
        
        # Standard prefixes
        self.standard_prefixes = {
            'rdf': RDF,
            'rdfs': RDFS,
            'owl': OWL,
            'xsd': XSD,
            'sh': SH,
            'dcterms': DCTERMS,
            'skos': SKOS,
        }
        
        # Default namespace
        self.GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#')
    
    def clean_content(self, content: str) -> str:
        """Clean the content by fixing common issues."""
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
    
    def load(self) -> None:
        """Load the TTL file into the graph."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                raise ValueError("Input file is empty")
            
            # Clean and preprocess content
            content = self.clean_content(content)
            
            # Add default prefix if not present
            if not '@prefix : <' in content:
                content = f'@prefix : <{str(self.GUIDANCE)}> .\n\n' + content
            
            # Parse the content
            self.graph.parse(data=content, format='turtle')
            logger.info("Successfully loaded file")
            
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
            raise
    
    def save(self) -> None:
        """Save the graph back to the TTL file."""
        try:
            # Serialize to string
            output: str = self.graph.serialize(format='turtle', encoding='utf-8').decode('utf-8')
            
            # Write to temporary file first
            with open(self.temp_path, 'w', encoding='utf-8') as f:
                f.write(output)
            
            # Move temporary file to final location
            shutil.move(self.temp_path, self.file_path)
            logger.info("Successfully saved file")
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            if Path(self.temp_path).exists():
                Path(self.temp_path).unlink()
            raise
    
    def fix_prefixes(self) -> None:
        """Fix prefix issues in the graph."""
        # Remove any numbered prefixes
        for prefix, ns in list(self.graph.namespaces()):
            if prefix.startswith('sh') and prefix != 'sh':
                self.graph.namespace_manager.bind(prefix, ns, override=True, replace=True)
        
        # Add standard prefixes
        for prefix, namespace in self.standard_prefixes.items():
            if prefix not in [p for p, n in self.graph.namespaces()]:
                self.graph.namespace_manager.bind(prefix, namespace)
        
        # Add default prefix if not present
        if '' not in [p for p, n in self.graph.namespaces()]:
            self.graph.namespace_manager.bind('', self.GUIDANCE)
    
    def add_triple(self, subject: str, predicate: str, object_: str, datatype: Optional[str] = None) -> None:
        """Add a triple to the graph."""
        s = URIRef(subject) if subject.startswith('http') else self.GUIDANCE[subject]
        p = URIRef(predicate) if predicate.startswith('http') else self.GUIDANCE[predicate]
        
        if datatype:
            o: Union[Literal, URIRef] = Literal(object_, datatype=URIRef(datatype))
        else:
            o = URIRef(object_) if object_.startswith('http') else self.GUIDANCE[object_]
        
        self.graph.add((s, p, o))
    
    def remove_triple(self, subject: str, predicate: str, object_: str) -> None:
        """Remove a triple from the graph."""
        s = URIRef(subject) if subject.startswith('http') else self.GUIDANCE[subject]
        p = URIRef(predicate) if predicate.startswith('http') else self.GUIDANCE[predicate]
        o = URIRef(object_) if object_.startswith('http') else self.GUIDANCE[object_]
        
        self.graph.remove((s, p, o))
    
    def backup(self) -> None:
        """Create a backup of the current file."""
        shutil.copy2(self.file_path, self.backup_path)
        logger.info(f"Created backup at {self.backup_path}")
    
    def restore_backup(self) -> None:
        """Restore from backup if it exists."""
        if Path(self.backup_path).exists():
            shutil.copy2(self.backup_path, self.file_path)
            logger.info("Restored from backup")
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        if Path(self.backup_path).exists():
            Path(self.backup_path).unlink()
        if Path(self.temp_path).exists():
            Path(self.temp_path).unlink()

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python rdf_editor.py <ttl_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    editor = RDFEditor(file_path)
    
    try:
        # Create backup
        editor.backup()
        
        # Load and process the file
        editor.load()
        editor.fix_prefixes()
        
        # Example: Add a new triple
        # editor.add_triple('MyClass', 'rdf:type', 'owl:Class')
        
        # Save changes
        editor.save()
        logger.info("Successfully processed file")
        
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {str(e)}")
        editor.restore_backup()
        sys.exit(1)
    finally:
        editor.cleanup()

if __name__ == '__main__':
    main() 