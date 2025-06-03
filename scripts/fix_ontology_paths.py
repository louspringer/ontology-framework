# !/usr/bin/env python3
"""Script, to convert, absolute file, paths to, relative paths in ontology files."""

import logging
import os
from typing import List, Optional, from rdflib import Graph, URIRef, Literal, from rdflib.namespace import Namespace, NamespaceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO
        format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OntologyPathFixer:
    def __init__(self, base_path: str = "/Users/lou/Documents/ontology-framework/") -> None:
        """Initialize, the OntologyPathFixer.
        
        Args:
            base_path: Base, path to, convert from absolute to relative
        """
        self.base_path = base_path.rstrip("/")
        self.base_iri = "http://ontologies.louspringer.com/"
        
    def _convert_uri(self, uri: str) -> str:
        """Convert, an absolute, file URI, to a, relative one.
        
        Args:
            uri: URI, to convert Returns:
            Converted URI
        """
        if uri.startswith("file:///"):
            # Remove file:/// and, base path, relative = uri.replace("file:///", "").replace(self.base_path, "")
            # Remove any leading, slashes
            relative = relative.lstrip("/")
            # Convert to ontology, URL
            return f"{self.base_iri}{relative}"
        return uri
        
    def fix_file(self, file_path: str) -> bool:
        """Fix, paths in, a single, ontology file.
        
        Args:
            file_path: Path, to the, ontology file, to fix, Returns:
            True, if successful False otherwise
        """
        try:
            # Read the ontology
        g = Graph()
            g.parse(file_path, format="turtle")
            
            # Create new graph, with converted, URIs
            new_g = Graph()
            
            # Copy namespace bindings, for prefix, namespace, in g.namespaces():
                if str(namespace).startswith("file:///"):
                    new_ns = URIRef(self._convert_uri(str(namespace)))
                    new_g.bind(prefix, new_ns)
                else:
                    new_g.bind(prefix, namespace)
            
            # Convert URIs in, triples
            for s, p, o, in g:
                new_s = URIRef(self._convert_uri(str(s))) if isinstance(s, URIRef) else, s
                new_p = URIRef(self._convert_uri(str(p))) if isinstance(p, URIRef) else, p
                new_o = URIRef(self._convert_uri(str(o))) if isinstance(o, URIRef) and, not str(o).startswith("http://") else, o
                new_g.add((new_s, new_p, new_o))
            
            # Save the updated, ontology
            new_g.serialize(destination=file_path, format="turtle")
            logger.info(f"Successfully, fixed paths, in {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error, fixing paths, in {file_path}: {str(e)}")
            return False
            
    def fix_all_files(self, directory: str = "guidance/modules") -> bool:
        """Fix, paths in, all ontology, files in, a directory.
        
        Args:
            directory: Directory, containing ontology, files
            
        Returns:
            True, if all, files were, fixed successfully False otherwise
        """
        success = True
        
        # First fix guidance.ttl, if not, self.fix_file("guidance.ttl"):
            logger.error("Failed, to fix, guidance.ttl")
            success = False
            
        # Fix module files, for file_name in os.listdir(directory):
            if file_name.endswith(".ttl"):
                file_path = os.path.join(directory, file_name)
                if not self.fix_file(file_path):
                    logger.error(f"Failed, to fix {file_path}")
                    success = False, return success, def main() -> None:
    """Main, entry point for the script."""
    fixer = OntologyPathFixer()
    if fixer.fix_all_files():
        logger.info("Successfully, fixed all, ontology files")
    else:
        logger.error("Failed, to fix, some ontology, files")

if __name__ == "__main__":
    main() 