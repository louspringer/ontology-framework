#!/usr/bin/env python3
"""CLI for ontology framework."""

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from pathlib import Path
import logging
from dotenv import load_dotenv

from .guidance_manager import GuidanceManager
from .graphdb_client import GraphDBClient
from .patch_management import GraphDBPatchManager
from .config import Config

# Load environment variables
load_dotenv()

# Initialize configuration
config = Config()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.get("logging.level", "INFO")),
    format=config.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger = logging.getLogger(__name__)

class CLI:
    """CLI application."""
    
    def __init__(self):
        self.config = Config()

pass_cli = click.make_pass_decorator(CLI, ensure=True)

@click.group()
@click.pass_context
def cli(ctx):
    """Ontology Framework CLI.
    
    A command-line interface for managing ontology framework guidance files.
    Provides commands for syncing, validating, and patching guidance files.
    """
    ctx.obj = CLI()

@cli.group()
def guidance():
    """Manage guidance files.
    
    Commands for managing guidance files in the ontology framework.
    Includes operations for syncing, validating, and patching files.
    """
    pass

@guidance.command()
@click.option("--auto-sync", is_flag=True, help="Automatically sync out-of-sync files")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def status(auto_sync: bool, verbose: bool):
    """Show guidance sync status.
    
    Displays the sync status of all guidance files.
    Shows which files are in sync and which need updating.
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    try:
        manager = GuidanceManager(GraphDBClient(), GraphDBPatchManager())
        manager.show_sync_status()
        
        if auto_sync:
            manager.auto_sync()
            manager.show_sync_status()
    except Exception as e:
        logger.error(f"Failed to check status: {e}")
        raise click.ClickException(str(e))

@guidance.command()
@click.argument("filename")
@click.option("--from-graphdb", is_flag=True, help="Sync from GraphDB to TTL")
@click.option("--to-graphdb", is_flag=True, help="Sync from TTL to GraphDB")
def sync(filename: str, from_graphdb: bool, to_graphdb: bool):
    """Sync a specific guidance file.
    
    Synchronizes a guidance file between the local TTL file and GraphDB.
    Must specify either --from-graphdb or --to-graphdb.
    """
    if not (from_graphdb or to_graphdb):
        raise click.ClickException("Must specify --from-graphdb or --to-graphdb")
        
    try:
        manager = GuidanceManager(GraphDBClient(), GraphDBPatchManager())
        if from_graphdb:
            manager.sync_from_graphdb(filename)
        else:
            manager.sync_to_graphdb(filename)
    except Exception as e:
        logger.error(f"Failed to sync {filename}: {e}")
        raise click.ClickException(str(e))

@guidance.command()
@click.argument("filename")
def diff(filename: str):
    """Show differences between TTL and GraphDB versions.
    
    Displays detailed differences between the local TTL file
    and its GraphDB counterpart.
    """
    try:
        manager = GuidanceManager(GraphDBClient(), GraphDBPatchManager())
        status = manager.check_sync_status()
        
        if filename not in status:
            raise click.ClickException(f"File {filename} not found")
            
        info = status[filename]
        console = Console()
        
        table = Table(title=f"Differences for {filename}")
        table.add_column("Property", style="cyan")
        table.add_column("TTL", style="green")
        table.add_column("GraphDB", style="magenta")
        
        # Add timestamp difference
        ttl_time = manager.get_ttl_timestamps().get(filename)
        graphdb_time = manager.get_graphdb_timestamps().get(filename)
        table.add_row(
            "Last Modified",
            ttl_time.strftime("%Y-%m-%d %H:%M:%S") if ttl_time else "N/A",
            graphdb_time.strftime("%Y-%m-%d %H:%M:%S") if graphdb_time else "N/A"
        )
        
        # Add source difference
        table.add_row(
            "Source",
            "TTL",
            "GraphDB"
        )
        
        console.print(table)
        
    except Exception as e:
        logger.error(f"Failed to show diff for {filename}: {e}")
        raise click.ClickException(str(e))

@guidance.command()
@click.argument("filename")
def validate(filename: str):
    """Validate a guidance file.
    
    Validates the syntax and structure of a guidance file.
    Checks for common issues and provides detailed feedback.
    """
    try:
        manager = GuidanceManager(GraphDBClient(), GraphDBPatchManager())
        manager.validate_file(filename)
        click.echo(f"✓ {filename} is valid")
    except Exception as e:
        logger.error(f"Validation failed for {filename}: {e}")
        raise click.ClickException(str(e))

@guidance.command()
@click.argument("filename")
@click.option("--dry-run", is_flag=True, help="Show what would be patched without applying changes")
def patch(filename: str, dry_run: bool):
    """Apply patches to a guidance file.
    
    Applies any pending patches to the specified guidance file.
    Use --dry-run to preview changes without applying them.
    """
    try:
        manager = GuidanceManager(GraphDBClient(), GraphDBPatchManager())
        if dry_run:
            manager.preview_patches(filename)
        else:
            manager.apply_patches(filename)
    except Exception as e:
        logger.error(f"Failed to patch {filename}: {e}")
        raise click.ClickException(str(e))

@cli.group()
def config():
    """Manage CLI configuration.
    
    Commands for viewing and modifying CLI settings.
    """
    pass

@config.command()
@click.argument("key")
@click.argument("value")
@pass_cli
def set(cli: CLI, key: str, value: str):
    """Set a configuration value.
    
    Updates a configuration setting with the specified value.
    """
    try:
        cli.config.set(key, value)
        click.echo(f"✓ Set {key} = {value}")
    except Exception as e:
        logger.error(f"Failed to set config: {e}")
        raise click.ClickException(str(e))

@config.command()
@click.argument("key")
@pass_cli
def get(cli: CLI, key: str):
    """Get a configuration value.
    
    Displays the current value of a configuration setting.
    """
    try:
        value = cli.config.get(key)
        click.echo(f"{key} = {value}")
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise click.ClickException(str(e))

@config.command()
@pass_cli
def show(cli: CLI):
    """Show all configuration settings.
    
    Displays all current configuration values.
    """
    try:
        console = Console()
        table = Table(title="Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        
        def add_config_section(section: str, data: dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    add_config_section(f"{section}.{key}", value)
                else:
                    table.add_row(f"{section}.{key}", str(value))
        
        for section, data in cli.config.config.items():
            add_config_section(section, data)
            
        console.print(table)
    except Exception as e:
        logger.error(f"Failed to show config: {e}")
        raise click.ClickException(str(e))

if __name__ == "__main__":
    cli() 