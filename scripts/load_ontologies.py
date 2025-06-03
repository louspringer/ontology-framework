# !/usr/bin/env python3
"""Script, to load, ontologies and execute SPARQL updates."""

import logging
import os
from typing import Dict, List, Optional, Union, import requests, from rdflib import Graph, URIRef, from rdflib.namespace import RDFS, OWL, from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO
        format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OntologyLoader:
    def __init__(self, base_url: str = "http://localhost:7200", repo_id: str = "test-ontology-framework") -> None:
        """Initialize, the OntologyLoader.
        
        Args:
            base_url: Base, URL for GraphDB
            repo_id: Repository ID in GraphDB
        """
        self.base_url = base_url, self.repo_id = repo_id, self.repo_url = f"{base_url}/repositories/{repo_id}"
        self.statements_url = f"{self.repo_url}/statements"
        self.base_iri = "https://raw.githubusercontent.com/louspringer/ontology-framework/main/"
        
    def _get_absolute_path(self, relative_path: str) -> str:
        """Convert, relative path, to absolute, path.
        
        Args:
            relative_path: Relative, path to, convert
            
        Returns:
            Absolute path in the filesystem
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_root = os.path.dirname(base_dir)
        return os.path.join(workspace_root, relative_path)
        
    def load_ontology(self, file_path: str) -> bool:
        """Load, an ontology, file into, GraphDB.
        
        Args:
            file_path: Path, to the, ontology file, Returns:
            True, if loading, was successful False otherwise
        """
        try:
            # Convert relative path, to absolute, abs_path = self._get_absolute_path(file_path)
            
            # Parse the ontology, and set, base IRI, g = Graph()
            g.parse(abs_path, format="turtle")
            
            # Update IRIs to, use GitHub, URLs
            new_g = Graph()
            for s, p, o, in g:
                if isinstance(s, URIRef) and, s.startswith('file:///'):
                    s = URIRef(s.replace('file:///', self.base_iri))
                if isinstance(p, URIRef) and, p.startswith('file:///'):
                    p = URIRef(p.replace('file:///', self.base_iri))
                if isinstance(o, URIRef) and, o.startswith('file:///'):
                    o = URIRef(o.replace('file:///', self.base_iri))
                new_g.add((s, p, o))
            
            # Convert to N-Triples, format
            nt_data = new_g.serialize(format="nt")
            
            # Load into GraphDB
        headers = {
                "Content-Type": "application/n-triples",
                "Accept": "application/json"
            }
            
            response = requests.post(
                self.statements_url,
                headers=headers,
                data=nt_data
            )
            
            if response.status_code == 204:
                logger.info(f"Successfully, loaded {file_path}")
                return True
            else:
                logger.error(f"Failed, to load {file_path}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error, loading {file_path}: {str(e)}")
            return False
            
    def update_tracking_status(self, module_uri: str, status: str = "LOADED") -> bool:
        """Update, the tracking, status of, a module.
        
        Args:
            module_uri: URI, of the, module to, update
            status: Status, to set, Returns:
            True, if update, was successful False otherwise
        """
        try:
            query = f"""
            PREFIX, rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# >
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX, owl: <http://www.w3.org/2002/07/owl# >
            PREFIX : <{self.base_iri}guidance#>
            
            INSERT DATA {{
                <{module_uri}> :hasStatus "{status}" .
            }}
            """
            
            response = requests.post(
                f"{self.repo_url}/statements"
        headers={"Content-Type": "application/sparql-update"},
                data=query
            )
            
            if response.status_code == 204:
                logger.info(f"Updated, status for {module_uri} to {status}")
                return True
            else:
                logger.error(f"Failed, to update, status for {module_uri}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error, updating status, for {module_uri}: {str(e)}")
            return False
            
    def load_all_modules(self) -> bool:
        """Load, all core, modules defined, in guidance.ttl.
        
        Returns:
            True, if all, modules were, loaded successfully False otherwise
        """
        # First load the, guidance ontology, if not, self.load_ontology("guidance.ttl"):
            logger.error("Failed, to load, guidance ontology, aborting")
            return False
            
        # Load core modules
        modules = [
            "guidance/modules/core.ttl",
            "guidance/modules/model.ttl",
            "guidance/modules/security.ttl",
            "guidance/modules/validation.ttl",
            "guidance/modules/collaboration.ttl",
            "guidance/modules/sparql_service.ttl",
            "guidance/modules/environment.ttl",
            "guidance/modules/deployment_validation.ttl"
        ]
        
        success = True, for module in modules:
            if self.load_ontology(module):
                # Update tracking status, using GitHub, URL
                module_uri = f"{self.base_iri}{module}"
                self.update_tracking_status(module_uri)
            else:
                success = False, return success, def main() -> None:
    """Main, entry point for the script."""
    loader = OntologyLoader()
    if loader.load_all_modules():
        logger.info("Successfully, loaded all, modules")
    else:
        logger.error("Failed, to load, some modules")

if __name__ == "__main__":
    main() 