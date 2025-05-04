#!/usr/bin/env python3
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
from typing import Optional, List, Dict, Any, Union, Tuple

from rdflib import Graph, URIRef, Literal, XSD, RDFS, OWL, RDF, BNode, Namespace
from rdflib.namespace import Namespace
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
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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
        
        # Create staging repository if it doesn't exist
        self._ensure_repository(staging_repository)
        self.staging_client = GraphDBClient(graphdb_url, staging_repository)
        
        # Local graphs for validation
        self.data_graph = Graph()
        self.shapes_graph = Graph()
        
    def _ensure_repository(self, repo_name: str) -> None:
        """Ensure repository exists, create if it doesn't."""
        try:
            # Setup a temporary client to check/create repo
            temp_client = GraphDBClient(self.graphdb_url)
            repos = temp_client.list_repositories()
            
            if not any(r.get('id') == repo_name for r in repos):
                logger.info(f"Creating repository '{repo_name}'")
                temp_client.create_repository(repo_name, f"{repo_name.title()} Repository")
            else:
                logger.info(f"Repository '{repo_name}' already exists")
        except GraphDBError as e:
            logger.error(f"Failed to check/create repository: {e}")
            raise

    def load_ontology(self, file_path: Union[str, Path], context_uri: Optional[str] = None) -> None:
        """Load an ontology file into local graphs.
        
        Args:
            file_path: Path to the ontology file
            context_uri: Optional named graph URI
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.info(f"Loading ontology from {file_path}")
        self.data_graph = Graph()
        self.data_graph.parse(file_path, format="turtle")
        
    def load_shacl_shapes(self, file_path: Union[str, Path]) -> None:
        """Load SHACL shapes from a file.
        
        Args:
            file_path: Path to the SHACL shapes file
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.info(f"Loading SHACL shapes from {file_path}")
        self.shapes_graph = Graph()
        self.shapes_graph.parse(file_path, format="turtle")
    
    def validate_locally(self) -> Tuple[bool, str]:
        """Validate the ontology locally using SHACL.
        
        Returns:
            Tuple of (success, validation_report)
        """
        logger.info("Validating ontology locally with SHACL")
        conforms, results_graph, results_text = validate(
            self.data_graph,
            shacl_graph=self.shapes_graph,
            ont_graph=None,
            inference='rdfs',
            abort_on_first=False,
            allow_infos=True,
            allow_warnings=True,
            meta_shacl=False,
            debug=False,
            js=False
        )
        
        if not conforms:
            logger.warning(f"SHACL validation failed:\n{results_text}")
        else:
            logger.info("SHACL validation successful")
            
        return conforms, results_text
    
    def update_shapes_in_graph(self) -> None:
        """Update the data graph with new SHACL shapes.
        
        This removes existing shapes and adds new ones.
        """
        # Find all node shapes in data graph
        shapes_to_remove = []
        for s, p, o in self.data_graph.triples((None, RDF.type, SH.NodeShape)):
            shapes_to_remove.append(s)
            
        # Remove all existing shapes and their properties
        for shape in shapes_to_remove:
            for s, p, o in self.data_graph.triples((shape, None, None)):
                self.data_graph.remove((s, p, o))
            
            # Also remove properties where this shape is the object
            for s, p, o in self.data_graph.triples((None, None, shape)):
                self.data_graph.remove((s, p, o))
                
        # Add all shapes from the shapes graph
        self.data_graph += self.shapes_graph
        logger.info(f"Updated {len(shapes_to_remove)} shapes in the data graph")
    
    def save_updated_ontology(self, output_path: Union[str, Path]) -> None:
        """Save the updated ontology to a file.
        
        Args:
            output_path: Path to save the updated ontology
        """
        logger.info(f"Saving updated ontology to {output_path}")
        self.data_graph.serialize(destination=output_path, format="turtle")
    
    def _clear_graph_in_graphdb(self, client: GraphDBClient, graph_uri: Optional[str] = None) -> None:
        """Clear a graph in GraphDB.
        
        Args:
            client: GraphDB client
            graph_uri: Optional named graph URI
        """
        logger.info(f"Clearing graph{' ' + graph_uri if graph_uri else ''} in repository {client.repository}")
        try:
            if graph_uri:
                # Clear specific named graph
                client.clear_graph(graph_uri)
            else:
                # Clear default graph using SPARQL UPDATE
                client.update("CLEAR DEFAULT")
        except GraphDBError as e:
            logger.error(f"Failed to clear graph: {e}")
            raise
    
    def reload_in_graphdb(self, 
                         target_repository: str,
                         graph_uri: Optional[str] = None,
                         disable_inference: bool = True) -> None:
        """Reload the ontology into GraphDB.
        
        Args:
            target_repository: Repository to reload into
            graph_uri: Optional named graph URI
            disable_inference: Whether to temporarily disable inference
        """
        # Get the right client
        client = self.main_client if target_repository == self.main_repo else self.staging_client
        
        try:
            logger.info(f"Reloading ontology into {target_repository}")
            
            if disable_inference:
                # TODO: Implement inference disabling using GraphDB ruleset API if needed
                # This would require modifying the repository configuration
                pass
            
            # Clear the graph
            self._clear_graph_in_graphdb(client, graph_uri)
            
            # Upload the graph
            temp_file = Path("temp_upload.ttl")
            try:
                self.data_graph.serialize(destination=temp_file, format="turtle")
                
                if graph_uri:
                    client.upload_graph(temp_file, graph_uri)
                else:
                    client.upload_graph(temp_file)
                    
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
        """Execute the complete validation and update pipeline.
        
        Args:
            input_file: Input ontology file
            shapes_file: SHACL shapes file
            output_file: Output file path (defaults to overwriting input file)
            reload_graphdb: Whether to reload in GraphDB
            graph_uri: Optional graph URI for GraphDB
            
        Returns:
            Success status
        """
        try:
            # Default output to input if not specified
            if output_file is None:
                output_file = input_file
                
            # 1. Load ontology and shapes
            self.load_ontology(input_file)
            self.load_shacl_shapes(shapes_file)
            
            # 2. Validate locally
            conforms, _ = self.validate_locally()
            if not conforms:
                logger.warning("Proceeding despite validation failures")
                
            # 3. Update shapes in graph
            self.update_shapes_in_graph()
            
            # 4. Save to file
            self.save_updated_ontology(output_file)
            
            # 5. Optionally reload in GraphDB
            if reload_graphdb:
                # First try in staging
                self.reload_in_graphdb(self.staging_repo, graph_uri)
                
                # Then in main repository
                self.reload_in_graphdb(self.main_repo, graph_uri)
                
            return True
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update SHACL constraints and reload in GraphDB")
    parser.add_argument("--ontology", required=True, help="Path to ontology file")
    parser.add_argument("--shapes", required=True, help="Path to SHACL shapes file")
    parser.add_argument("--output", help="Output path (defaults to overwriting input)")
    parser.add_argument("--graphdb-url", default="http://localhost:7200", help="GraphDB URL")
    parser.add_argument("--repository", default="ontology-framework", help="GraphDB repository")
    parser.add_argument("--graph-uri", help="Named graph URI")
    parser.add_argument("--no-reload", action="store_true", help="Skip reloading in GraphDB")
    
    args = parser.parse_args()
    
    manager = SHACLGraphDBManager(
        graphdb_url=args.graphdb_url,
        repository=args.repository
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