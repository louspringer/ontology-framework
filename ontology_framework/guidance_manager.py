#!/usr/bin/env python3
"""Guidance manager for ontology framework."""

from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS
import logging
from datetime import datetime
import os
import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .graphdb_client import GraphDBClient
from .patch_management import GraphDBPatchManager

# Define namespaces
GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")

class GuidanceManager:
    """Manages guidance synchronization between TTL files and GraphDB."""
    
    def __init__(self, 
                 graphdb_client: GraphDBClient,
                 patch_manager: GraphDBPatchManager,
                 guidance_dir: Union[str, Path] = "guidance"):
        """Initialize guidance manager.
        
        Args:
            graphdb_client: GraphDB client instance
            patch_manager: Patch manager instance
            guidance_dir: Directory containing guidance TTL files
        """
        self.graphdb_client = graphdb_client
        self.patch_manager = patch_manager
        self.guidance_dir = Path(guidance_dir)
        self.logger = logging.getLogger(__name__)
        self._guidance_source = "TTL"  # Default to TTL files
        self.console = Console()
        
    def get_ttl_timestamps(self) -> Dict[str, datetime]:
        """Get last modified timestamps for TTL files.
        
        Returns:
            Dictionary mapping TTL file names to their last modified timestamps
        """
        timestamps = {}
        for ttl_file in self.guidance_dir.glob("**/*.ttl"):
            mtime = os.path.getmtime(ttl_file)
            timestamps[ttl_file.name] = datetime.fromtimestamp(mtime)
            self.logger.debug(f"TTL file {ttl_file.name} last modified: {timestamps[ttl_file.name]}")
        return timestamps
        
    def get_graphdb_timestamps(self) -> Dict[str, datetime]:
        """Get last modified timestamps from GraphDB logs.
        
        Returns:
            Dictionary mapping repository names to their last modified timestamps
        """
        timestamps = {}
        try:
            # Query GraphDB logs for last modification times
            query = """
            SELECT ?repo ?time
            WHERE {
                ?patch a <http://www.w3.org/ns/prov#Activity> ;
                       <http://www.w3.org/ns/prov#startedAtTime> ?time ;
                       <http://www.w3.org/ns/prov#used> ?repo .
            }
            ORDER BY DESC(?time)
            """
            results = self.graphdb_client.query("system", query)
            
            for result in results:
                repo = result["repo"]
                time = datetime.fromisoformat(result["time"])
                if repo not in timestamps or time > timestamps[repo]:
                    timestamps[repo] = time
                    self.logger.debug(f"GraphDB repo {repo} last modified: {time}")
                    
        except Exception as e:
            self.logger.error(f"Failed to get GraphDB timestamps: {e}")
            
        return timestamps
        
    def get_latest_source(self, filename: str) -> Tuple[str, datetime]:
        """Get the latest source and timestamp for a guidance file.
        
        Args:
            filename: Name of the guidance file
            
        Returns:
            Tuple of (source, timestamp) where source is "TTL" or "GraphDB"
        """
        ttl_timestamps = self.get_ttl_timestamps()
        graphdb_timestamps = self.get_graphdb_timestamps()
        
        ttl_time = ttl_timestamps.get(filename)
        graphdb_time = graphdb_timestamps.get(filename)
        
        if not ttl_time and not graphdb_time:
            self.logger.warning(f"No timestamps found for {filename}")
            return ("TTL", datetime.min)
        elif not ttl_time:
            self.logger.info(f"Only GraphDB timestamp found for {filename}: {graphdb_time}")
            return ("GraphDB", graphdb_time)
        elif not graphdb_time:
            self.logger.info(f"Only TTL timestamp found for {filename}: {ttl_time}")
            return ("TTL", ttl_time)
        else:
            source = "GraphDB" if graphdb_time > ttl_time else "TTL"
            latest_time = max(graphdb_time, ttl_time)
            time_diff = abs((graphdb_time - ttl_time).total_seconds())
            if time_diff > 60:  # More than 1 minute difference
                self.logger.warning(
                    f"Significant time difference for {filename}: "
                    f"GraphDB={graphdb_time}, TTL={ttl_time}, diff={time_diff}s"
                )
            return (source, latest_time)
                    
    def check_sync_status(self) -> Dict[str, Dict[str, Union[str, datetime]]]:
        """Check synchronization status of all guidance files.
        
        Returns:
            Dictionary mapping filenames to their sync status
        """
        status = {}
        for ttl_file in self.guidance_dir.glob("**/*.ttl"):
            source, timestamp = self.get_latest_source(ttl_file.name)
            status[ttl_file.name] = {
                "source": source,
                "timestamp": timestamp,
                "needs_sync": source != self._guidance_source
            }
        return status
        
    def auto_sync(self) -> None:
        """Automatically sync guidance files that are out of sync."""
        status = self.check_sync_status()
        for filename, info in status.items():
            if info["needs_sync"]:
                self.logger.info(f"Auto-syncing {filename} from {info['source']}")
                if info["source"] == "GraphDB":
                    self.sync_from_graphdb(filename)
                else:
                    self.sync_to_graphdb(filename)
                    
    def sync_from_graphdb(self, filename: str) -> None:
        """Sync a file from GraphDB to TTL."""
        try:
            repo = filename.replace(".ttl", "")
            query = """
            SELECT ?s ?p ?o
            WHERE {
                ?s ?p ?o
            }
            """
            results = self.graphdb_client.query(repo, query)
            
            ttl_file = self.guidance_dir / filename
            graph = Graph()
            for result in results:
                s, p, o = result
                graph.add((URIRef(s), URIRef(p), URIRef(o)))
                
            graph.serialize(ttl_file, format="turtle")
            self.logger.info(f"Synced {filename} from GraphDB to TTL")
            
        except Exception as e:
            self.logger.error(f"Failed to sync {filename} from GraphDB: {e}")
            
    def sync_to_graphdb(self, filename: str) -> None:
        """Sync a file from TTL to GraphDB."""
        try:
            repo = filename.replace(".ttl", "")
            ttl_file = self.guidance_dir / filename
            
            with open(ttl_file, 'r') as f:
                content = f.read()
                self.graphdb_client.import_data(
                    repo,
                    content,
                    context=f"guidance/{repo}"
                )
                
            self.logger.info(f"Synced {filename} from TTL to GraphDB")
            
        except Exception as e:
            self.logger.error(f"Failed to sync {filename} to GraphDB: {e}")
            
    def show_sync_status(self) -> None:
        """Display sync status in a formatted table."""
        status = self.check_sync_status()
        
        table = Table(title="Guidance Sync Status")
        table.add_column("File", style="cyan")
        table.add_column("Source", style="magenta")
        table.add_column("Last Modified", style="green")
        table.add_column("Needs Sync", style="red")
        
        for filename, info in status.items():
            table.add_row(
                filename,
                info["source"],
                info["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                "Yes" if info["needs_sync"] else "No"
            )
            
        self.console.print(table)
        
@click.group()
def cli():
    """Guidance management CLI."""
    pass

@cli.command()
@click.option("--auto-sync", is_flag=True, help="Automatically sync out-of-sync files")
def status(auto_sync: bool):
    """Show guidance sync status."""
    manager = GuidanceManager(GraphDBClient(), GraphDBPatchManager())
    manager.show_sync_status()
    
    if auto_sync:
        manager.auto_sync()
        manager.show_sync_status()

if __name__ == "__main__":
    cli() 