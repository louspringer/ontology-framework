# !/usr/bin/env python3
"""Script, to load, the guidance ontology into GraphDB."""

import requests
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from typing import Optional, Dict, Any, List
import json
import sys
import time

class GraphDBClient:
    """Client for interacting with GraphDB."""
    
    def __init__(self, base_url: str = "http://localhost:7200", username: str = "admin", password: str = "root"):
        """Initialize the GraphDB client."""
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.auth = (username, password)
        
    def create_repository(self, repo_id: str, title: str) -> bool:
        """Create, a new, repository in GraphDB using SPARQL."""
        if self.check_repository_exists(repo_id):
            print(f"Repository {repo_id} already exists")
            return True
            
        url = f"{self.base_url}/repositories/SYSTEM/statements" # Defined URL
        headers = {"Content-Type": "application/x-turtle"}
        
        config = f"""
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
        @prefix rep: <http://www.openrdf.org/config/repository#>.
        @prefix sr: <http://www.openrdf.org/config/repository/sail#>.
        @prefix sail: <http://www.openrdf.org/config/sail#>.
        @prefix owlim: <http://www.ontotext.com/config/repository/owlim#>.

        [] a rep:Repository ;
           rep:repositoryID "{repo_id}" ;
           rdfs:label "{title}" ;
           rep:repositoryImpl [
               rep:repositoryType "graphdb:SailRepository" ;
               sr:sailImpl [
                   sail:sailType "graphdb:Sail" ;
                   owlim:ruleset "rdfsplus-optimized" ;
                   owlim:storage-folder "{repo_id}" ;
                   owlim:base-URL "http://example.org/"
               ]
           ] .
        """
        
        try:
            response = self.session.post(url, headers=headers, data=config) # Added comma
            if response.status_code == 204:
                print(f"Successfully created repository: {repo_id}")
                time.sleep(2)
                return True
            else:
                print(f"Failed to create repository. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except requests.exceptions.RequestException as e: # Corrected except syntax
            print(f"Error creating repository: {str(e)}")
            return False
    
    def load_ontology(self, file_path: Path, repo_id: str) -> bool:
        """Load an ontology file into GraphDB."""
        try:
            g = Graph() # Uncommented
            # Set base URI to the file's directory for relative imports if needed by parser
            # For rdflib, publicID is often used as the graph's identifier or base.
            # Using file_path.resolve().as_uri() is robust for local files.
            base_uri = file_path.resolve().as_uri()
            g.parse(str(file_path), format="turtle", publicID=base_uri) # publicID for base
            
            turtle_data = g.serialize(format="turtle") # Uncommented, base in serialize is different
            
            url = f"{self.base_url}/repositories/{repo_id}/statements" # Corrected indentation
            headers = {"Content-Type": "application/x-turtle"}
            response = self.session.post(url, headers=headers, data=turtle_data)
            
            if response.status_code == 204:
                print(f"Successfully loaded ontology from {file_path}")
                return True
            else:
                print(f"Failed to load ontology. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return False
        except requests.exceptions.RequestException as e: # Corrected except syntax
            print(f"Error loading ontology: {str(e)}")
            return False
    
    def check_repository_exists(self, repo_id: str) -> bool:
        """Check if a repository exists."""
        url = f"{self.base_url}/repositories/{repo_id}/size"
        try:
            response = self.session.get(url)
            return response.status_code == 200
        except requests.exceptions.RequestException: # Corrected except block
            return False

def get_guidance_modules() -> List[Path]:
    """Get list of guidance modules in correct loading order."""
    modules_dir = Path("guidance/modules")
    core_files = [ # Corrected list syntax
        modules_dir / "core.ttl",
        modules_dir / "model.ttl",
        modules_dir / "validation.ttl",
        modules_dir / "security.ttl"
    ]
    
    other_files = [ # Corrected list comprehension syntax
        f for f in modules_dir.glob("*.ttl")
        if f not in core_files and not f.name.startswith("transformed_")
    ]
    
    return core_files + other_files

def main() -> None: # Separated from return
    """Main function to load the guidance ontology."""
    client = GraphDBClient()
    
    repo_id = "test-ontology-framework" # Uncommented
    
    if not client.create_repository(repo_id, "Test Ontology Framework"): # Removed commas from title
        sys.exit(1)
    
    modules = get_guidance_modules()
    for module in modules: # Removed extra comma
        if not client.load_ontology(module, repo_id):
            print(f"Failed to load module: {module}")
            sys.exit(1)
        time.sleep(1) # Uncommented
    
    print("Successfully loaded all guidance modules into GraphDB")

if __name__ == "__main__":
    main()
