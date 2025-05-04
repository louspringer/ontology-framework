#!/usr/bin/env python3
"""
Script for managing materialized inference in GraphDB repositories.

This script provides utilities to:
1. Temporarily disable/enable inference in a GraphDB repository
2. Clear only inferred statements without affecting explicit triples
3. Export/import repository with controlled inference settings

These operations help manage the challenges of working with materialized inference
and SHACL validation in GraphDB, especially when updating constraints.
"""

import argparse
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

import requests
from rdflib import Graph

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


class InferenceManager:
    """Manager for GraphDB inference operations."""

    def __init__(self, graphdb_url: str = "http://localhost:7200", repository: str = "ontology-framework"):
        """Initialize the inference manager.
        
        Args:
            graphdb_url: GraphDB server URL
            repository: Repository name
        """
        self.graphdb_url = graphdb_url
        self.repository = repository
        self.client = GraphDBClient(graphdb_url, repository)
        
    def get_current_ruleset(self) -> str:
        """Get the current inference ruleset for the repository.
        
        Returns:
            Current ruleset name
        """
        try:
            # Query GraphDB for repository configuration
            response = requests.get(
                f"{self.graphdb_url}/rest/repositories/{self.repository}/info",
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            
            info = response.json()
            ruleset = info.get("ruleset", "")
            
            logger.info(f"Current ruleset for repository '{self.repository}': {ruleset}")
            return ruleset
        except Exception as e:
            logger.error(f"Failed to get ruleset: {e}")
            raise
    
    def change_ruleset(self, new_ruleset: str) -> bool:
        """Change the inference ruleset for the repository.
        
        Args:
            new_ruleset: New ruleset name to set
                Valid options: 
                - "empty" (no inference)
                - "rdfs" (basic RDFS inference)
                - "rdfsplus" (RDFS+ with extended properties)
                - "owl-horst" (OWL with Horst optimizations)
                - "owl-max" (maximum OWL inference)
                - "owl2-ql" (OWL2 QL profile)
                - "owl2-rl" (OWL2 RL profile)
                
        Returns:
            Success status
        """
        try:
            # Get current repository configuration
            response = requests.get(
                f"{self.graphdb_url}/rest/repositories/{self.repository}/config",
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            
            config = response.json()
            
            # Modify the ruleset
            if "params" in config:
                config["params"]["ruleset"] = new_ruleset
                
            # Update repository configuration
            # Note: This will restart the repository
            response = requests.post(
                f"{self.graphdb_url}/rest/repositories/{self.repository}/config",
                json=config,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            logger.info(f"Changed ruleset for repository '{self.repository}' to '{new_ruleset}'")
            return True
        except Exception as e:
            logger.error(f"Failed to change ruleset: {e}")
            return False
    
    def disable_inference(self) -> str:
        """Disable inference by changing to empty ruleset.
        
        Returns:
            Previous ruleset name
        """
        previous_ruleset = self.get_current_ruleset()
        if previous_ruleset != "empty":
            self.change_ruleset("empty")
            logger.info(f"Disabled inference (previous ruleset: {previous_ruleset})")
        else:
            logger.info("Inference already disabled")
            
        return previous_ruleset
    
    def enable_inference(self, ruleset: str = "owl-horst-optimized") -> bool:
        """Enable inference with the specified ruleset.
        
        Args:
            ruleset: Ruleset to enable
            
        Returns:
            Success status
        """
        current_ruleset = self.get_current_ruleset()
        if current_ruleset == "empty":
            success = self.change_ruleset(ruleset)
            if success:
                logger.info(f"Enabled inference with ruleset '{ruleset}'")
            return success
        else:
            logger.info(f"Inference already enabled with ruleset '{current_ruleset}'")
            return True
    
    def clear_inferred_statements(self) -> bool:
        """Clear only inferred statements from the repository.
        
        This is done by:
        1. Backing up explicit statements 
        2. Clearing the repository
        3. Restoring only explicit statements
        
        Returns:
            Success status
        """
        try:
            logger.info(f"Clearing inferred statements from repository '{self.repository}'")
            
            # 1. First, disable inference to avoid materialization during operations
            previous_ruleset = self.disable_inference()
            
            # 2. Export explicit statements to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".ttl", delete=False) as temp_file:
                temp_path = temp_file.name
                
            # Get explicit statements
            response = requests.get(
                f"{self.graphdb_url}/repositories/{self.repository}/statements",
                headers={"Accept": "text/turtle"}
            )
            response.raise_for_status()
            
            # Save to temp file
            with open(temp_path, "wb") as f:
                f.write(response.content)
                
            logger.info(f"Exported explicit statements to {temp_path}")
            
            # 3. Clear the repository
            self.client.update("CLEAR ALL")
            logger.info("Cleared all statements from repository")
            
            # 4. Reload the explicit statements
            with open(temp_path, "rb") as f:
                response = requests.post(
                    f"{self.graphdb_url}/repositories/{self.repository}/statements",
                    data=f,
                    headers={"Content-Type": "text/turtle"}
                )
                response.raise_for_status()
                
            logger.info("Restored explicit statements")
            
            # 5. Re-enable inference if it was previously enabled
            if previous_ruleset != "empty":
                self.enable_inference(previous_ruleset)
                
            # 6. Clean up
            try:
                os.unlink(temp_path)
            except OSError:
                pass
                
            return True
        except Exception as e:
            logger.error(f"Failed to clear inferred statements: {e}")
            return False
    
    def separate_inferred_explicit(self) -> dict:
        """Get counts of explicit vs. inferred triples.
        
        Returns:
            Dictionary with counts
        """
        try:
            # Get current ruleset
            current_ruleset = self.get_current_ruleset()
            
            # Count all statements with inference
            all_count = self.client.count_triples()
            
            # Disable inference and count explicit statements
            self.disable_inference()
            explicit_count = self.client.count_triples()
            
            # Calculate inferred statements
            inferred_count = all_count - explicit_count
            
            # Restore previous ruleset
            if current_ruleset != "empty":
                self.enable_inference(current_ruleset)
                
            result = {
                "total": all_count,
                "explicit": explicit_count,
                "inferred": inferred_count,
                "ruleset": current_ruleset
            }
            
            logger.info(f"Statement counts: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to separate statements: {e}")
            raise
    
    def export_without_inference(self, output_file: Union[str, Path]) -> bool:
        """Export repository data without materialized inference.
        
        Args:
            output_file: Path to save the exported data
            
        Returns:
            Success status
        """
        try:
            output_file = Path(output_file)
            
            # Get current ruleset
            current_ruleset = self.get_current_ruleset()
            
            # Temporarily disable inference
            self.disable_inference()
            
            # Export data
            with open(output_file, "wb") as f:
                response = requests.get(
                    f"{self.graphdb_url}/repositories/{self.repository}/statements",
                    headers={"Accept": "text/turtle"}
                )
                response.raise_for_status()
                f.write(response.content)
                
            logger.info(f"Exported repository data without inference to {output_file}")
            
            # Restore previous ruleset
            if current_ruleset != "empty":
                self.enable_inference(current_ruleset)
                
            return True
        except Exception as e:
            logger.error(f"Failed to export repository: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Manage GraphDB inference")
    parser.add_argument("--graphdb-url", default="http://localhost:7200", help="GraphDB URL")
    parser.add_argument("--repository", default="ontology-framework", help="GraphDB repository")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Disable inference command
    disable_parser = subparsers.add_parser("disable", help="Disable inference")
    
    # Enable inference command
    enable_parser = subparsers.add_parser("enable", help="Enable inference")
    enable_parser.add_argument("--ruleset", default="owl-horst-optimized", help="Inference ruleset to enable")
    
    # Clear inferred statements command
    clear_parser = subparsers.add_parser("clear-inferred", help="Clear only inferred statements")
    
    # Get statement counts command
    count_parser = subparsers.add_parser("count", help="Get counts of explicit vs. inferred statements")
    
    # Export without inference command
    export_parser = subparsers.add_parser("export", help="Export repository data without inference")
    export_parser.add_argument("--output", required=True, help="Output file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    manager = InferenceManager(args.graphdb_url, args.repository)
    
    if args.command == "disable":
        manager.disable_inference()
    elif args.command == "enable":
        manager.enable_inference(args.ruleset)
    elif args.command == "clear-inferred":
        manager.clear_inferred_statements()
    elif args.command == "count":
        counts = manager.separate_inferred_explicit()
        print(f"Repository: {args.repository}")
        print(f"Ruleset: {counts['ruleset']}")
        print(f"Total statements: {counts['total']}")
        print(f"Explicit statements: {counts['explicit']}")
        print(f"Inferred statements: {counts['inferred']}")
    elif args.command == "export":
        manager.export_without_inference(args.output)
        
    sys.exit(0)


if __name__ == "__main__":
    main() 