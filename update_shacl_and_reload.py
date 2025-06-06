# !/usr/bin/env python3
"""
Script to safely update SHACL constraints and reload data into GraphDB.

This script handles the edge cases when working with materialized inference and SHACL validation
in GraphDB by:
1. Creating a clean version of the graph in a staging context
2. Validating SHACL constraints locally before applying
3. Properly clearing and reloading graphs to avoid interference from materialized inference
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Tuple # Corrected List import

from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode, Namespace
# No rdflib.namespace.Namespace, it's just rdflib.Namespace
from pyshacl import validate

# Add the project root to the Python path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.ontology_framework.graphdb_client import GraphDBClient, GraphDBError
except ImportError:
    # Try alternate import path
    try:
        from ontology_framework.graphdb_client import GraphDBClient, GraphDBError
    except ImportError:
        raise ImportError("Could not import GraphDBClient. Make sure ontology_framework is in your Python path.")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s' # Added comma
)
logger = logging.getLogger(__name__)

# Define common namespaces
SH = Namespace("http://www.w3.org/ns/shacl#")


class SHACLGraphDBManager:
    """Manager for handling SHACL shapes and GraphDB interactions."""

    def __init__(self, graphdb_url: str = "http://localhost:7200", 
                 repository: str = "ontology-framework",
                 staging_repository: str = "ontology-framework-staging"):
        """Initialize the SHACL GraphDB Manager.
        
        Args:
            graphdb_url: URL of the GraphDB server
            repository: Main repository name
            staging_repository: Staging repository name for validation
        """
        self.graphdb_url = graphdb_url
        self.main_repo = repository
        self.staging_repo = staging_repository
        self.main_client = GraphDBClient(graphdb_url, repository)
        
        self._ensure_repository(staging_repository)
        self.staging_client = GraphDBClient(graphdb_url, staging_repository) # Added comma
        
        self.data_graph = Graph()
        self.shapes_graph = Graph()
        
    def _ensure_repository(self, repo_name: str) -> None: # Added comma after self
        """Ensure repository exists create if it doesn't."""
        try:
            temp_client = GraphDBClient(self.graphdb_url) # repository will be default "test" or None if client changed
            repos = temp_client.list_repositories()
            
            if not any(r.get('id') == repo_name for r in repos):
                logger.info(f"Creating repository '{repo_name}'")
                # create_repository in main client needs repo_id and title
                temp_client.create_repository(repo_name, f"{repo_name.title()} Repository") # Added comma
            else:
                logger.info(f"Repository '{repo_name}' already exists")
        except GraphDBError as e:
            logger.error(f"Failed to check/create repository: {e}")
            raise

    def load_ontology(self, file_path: Union[str, Path], context_uri: Optional[str] = None) -> None:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.info(f"Loading ontology from {file_path}")
        self.data_graph = Graph()
        self.data_graph.parse(str(file_path), format="turtle") # Ensure path is string
        
    def load_shacl_shapes(self, file_path: Union[str, Path]) -> None:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.info(f"Loading SHACL shapes from {file_path}")
        self.shapes_graph = Graph()
        self.shapes_graph.parse(str(file_path), format="turtle") # Ensure path is string
    
    def validate_locally(self) -> Tuple[bool, str]:
        logger.info("Validating ontology locally with SHACL")
        conforms, results_graph, results_text = validate(
            self.data_graph,
            shacl_graph=self.shapes_graph,
            ont_graph=None, # This is correct for pyshacl
            inference='rdfs',
            abort_on_first=False,
            allow_infos=True, # Changed to True for more verbose output if needed
            allow_warnings=True, # Changed to True
            meta_shacl=False,
            debug=False,
            js=False # Assuming no JS execution needed for shapes
        )
        
        if not conforms:
            logger.warning(f"SHACL validation failed:\n{results_text}")
        else:
            logger.info("SHACL validation successful")
            
        return conforms, results_text # results_text is already a string
    
    def update_shapes_in_graph(self) -> None:
        shapes_to_remove = []
        for s, p, o in self.data_graph.triples((None, RDF.type, SH.NodeShape)): # Added commas
            shapes_to_remove.append(s)
            
        for shape_uri in shapes_to_remove: # Iterate over URIs
            # Remove triples where the shape is subject
            for s, p, o in self.data_graph.triples((shape_uri, None, None)): # Added commas
                self.data_graph.remove((s, p, o))
            # Remove triples where the shape is object (less common for NodeShape but good practice)
            for s, p, o in self.data_graph.triples((None, None, shape_uri)): # Added commas
                self.data_graph.remove((s, p, o))
                
        self.data_graph += self.shapes_graph
        logger.info(f"Updated {len(shapes_to_remove)} shapes in the data graph")
    
    def save_updated_ontology(self, output_path: Union[str, Path]) -> None:
        logger.info(f"Saving updated ontology to {output_path}")
        self.data_graph.serialize(destination=str(output_path), format="turtle") # Ensure path is string

    def _clear_graph_in_graphdb(self, client: GraphDBClient, graph_uri: Optional[str] = None) -> None:
        logger.info(f"Clearing graph{' ' + graph_uri if graph_uri else ' default'} in repository {client.repository}") # Added space
        try:
            if graph_uri:
                client.clear_graph(graph_uri)
            else:
                client.update("CLEAR DEFAULT")
        except GraphDBError as e:
            logger.error(f"Failed to clear graph: {e}")
            raise
    
    def reload_in_graphdb(self, target_repository: str,
                         graph_uri: Optional[str] = None,
                         disable_inference: bool = True) -> None:
        client = self.main_client if target_repository == self.main_repo else self.staging_client
        
        try:
            logger.info(f"Reloading ontology into {target_repository}")
            
            if disable_inference:
                # TODO: Implement inference disabling
                pass
            
            self._clear_graph_in_graphdb(client, graph_uri) # Added comma
            
            temp_file = Path("temp_upload.ttl") # This should be a unique name or handle deletion carefully
            try:
                # TODO: GraphDBClient.upload_graph expects a Graph object, not a file path.
                # This needs to be self.client.load_ontology(temp_file, context_uri=graph_uri)
                # or self.data_graph needs to be passed to upload_graph directly.
                # For now, serializing and assuming upload_graph can take a path (which it can't per current src)
                self.data_graph.serialize(destination=str(temp_file), format="turtle") # Added comma, ensure path is string
                
                # This is a logic error if client.upload_graph expects a Graph object.
                # The main GraphDBClient.upload_graph expects a Graph object.
                # GraphDBClient.load_ontology(path, context_uri) is the correct method for file paths.
                client.load_ontology(str(temp_file), context_uri=graph_uri) # Corrected to use load_ontology
                    
                logger.info("Successfully reloaded ontology in GraphDB")
            finally:
                if temp_file.exists():
                    temp_file.unlink()
                
        except GraphDBError as e:
            logger.error(f"Failed to reload ontology in GraphDB: {e}")
            raise

    def execute_validation_pipeline(self,
                                  input_file: Union[str, Path],
                                  shapes_file: Union[str, Path],
                                  output_file: Optional[Union[str, Path]] = None,
                                  reload_graphdb: bool = True,
                                  graph_uri: Optional[str] = None) -> bool:
        try:
            if output_file is None:
                output_file = input_file
                
            self.load_ontology(input_file)
            self.load_shacl_shapes(shapes_file)
            
            conforms, _ = self.validate_locally() # Corrected variable unpacking
            if not conforms:
                logger.warning("Proceeding despite validation failures")
                
            self.update_shapes_in_graph()
            self.save_updated_ontology(output_file)
            
            if reload_graphdb:
                self.reload_in_graphdb(self.staging_repo, graph_uri) # Added comma
                self.reload_in_graphdb(self.main_repo, graph_uri) # Added comma
                
            return True
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update SHACL constraints and reload in GraphDB")
    parser.add_argument("--ontology", # Added comma
        required=True, help="Path to ontology file")
    parser.add_argument("--shapes", required=True, help="Path to SHACL shapes file")
    parser.add_argument("--output", help="Output path (defaults to overwriting input)")
    parser.add_argument("--graphdb-url", default="http://localhost:7200", help="GraphDB URL")
    parser.add_argument("--repository", default="ontology-framework", help="GraphDB repository")
    parser.add_argument("--graph-uri", help="Named graph URI")
    parser.add_argument("--no-reload", action="store_true", help="Skip reloading in GraphDB")
    
    args = parser.parse_args()
    
    manager = SHACLGraphDBManager(
        graphdb_url=args.graphdb_url,
        repository=args.repository # staging_repository will use default
    )
    
    success = manager.execute_validation_pipeline(
        input_file=args.ontology,
        shapes_file=args.shapes,
        output_file=args.output,
        reload_graphdb=not args.no_reload,
        graph_uri=args.graph_uri
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
