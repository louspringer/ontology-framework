#!/usr/bin/env python3
"""Main CLI entry point for the ontology framework."""

import click
from pathlib import Path
from typing import Optional
import json

@click.group()
def cli() -> None:
    """Ontology Framework CLI."""
    pass

@cli.command()
@click.option(
    "--ontology",
    "-o",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to the ontology file"
)
@click.option(
    "--targets",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    multiple=True,
    required=True,
    help="Target files to analyze"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output"
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=".cursor/mcp.json",
    help="Path to MCP configuration file"
)
def mcp(ontology: Path, targets: tuple[Path, ...], verbose: bool, config: Path) -> None:
    """Model Context Protocol prompt pattern."""
    from ..modules.mcp_prompt import PromptContext, MCPPrompt
    
    # Load configuration
    with open(config) as f:
        config_data = json.load(f)
    
    # Set up the context
    context = PromptContext(
        ontology_path=ontology,
        target_files=list(targets),
        validation_rules=config_data.get("validationRules", {}),
        metadata={
            "ontologyPath": str(ontology),
            "targetFiles": [str(t) for t in targets],
            "validation": config_data.get("validation", {}),
            "mcpServers": config_data.get("mcpServers", {})
        }
    )
    
    # Create and execute the MCP prompt
    prompt = MCPPrompt(context)
    results = prompt.execute()
    
    # Print the results
    click.echo("\n=== MCP Prompt Results ===")
    
    # Discovery Phase Results
    click.echo("\nDiscovery Phase:")
    discovery = results["discovery"]
    click.echo(f"Classes found: {len(discovery['ontology_analysis']['classes'])}")
    click.echo(f"Properties found: {len(discovery['ontology_analysis']['properties'])}")
    click.echo(f"Data properties found: {len(discovery['ontology_analysis']['data_properties'])}")
    click.echo(f"Individuals found: {len(discovery['ontology_analysis']['individuals'])}")
    click.echo(f"SHACL shapes found: {len(discovery['ontology_analysis']['shapes'])}")
    
    if verbose:
        click.echo("\nDetailed Class Information:")
        for cls in discovery['ontology_analysis']['classes']:
            click.echo(f"  - {cls}")
        click.echo("\nDetailed Property Information:")
        for prop in discovery['ontology_analysis']['properties']:
            click.echo(f"  - {prop}")
    
    # File Analysis
    click.echo("\nFile Analysis:")
    for file_info in discovery["file_analysis"]:
        click.echo(f"\nFile: {file_info['file']}")
        click.echo(f"Exists: {file_info['exists']}")
        if file_info["exists"]:
            click.echo(f"Size: {file_info['size']} bytes")
            click.echo(f"Last Modified: {file_info['modified']}")
    
    # Plan Phase Results
    click.echo("\nPlan Phase:")
    plan = results["plan"]
    click.echo(f"Classes to process: {len(plan['classes'])}")
    click.echo(f"Properties to process: {len(plan['properties'])}")
    
    if verbose:
        click.echo("\nClasses to Process:")
        for cls in plan['classes']:
            click.echo(f"  - {cls}")
        click.echo("\nProperties to Process:")
        for prop in plan['properties']:
            click.echo(f"  - {prop}")
    
    # Do Phase Results
    click.echo("\nDo Phase:")
    do = results["do"]
    click.echo(f"Generated files: {len(do['generated_files'])}")
    click.echo(f"Modified files: {len(do['modified_files'])}")
    
    if verbose and do['modified_files']:
        click.echo("\nModified Files:")
        for file in do['modified_files']:
            click.echo(f"  - {file}")
    
    # Check Phase Results
    click.echo("\nCheck Phase:")
    check = results["check"]
    click.echo(f"Validation results: {len(check['validation_results'])}")
    click.echo(f"Test results: {len(check['test_results'])}")
    
    if verbose and check['validation_results']:
        click.echo("\nValidation Results:")
        for result in check['validation_results']:
            click.echo(f"  - {result['file']}: {result['status']}")
    
    # Act Phase Results
    click.echo("\nAct Phase:")
    act = results["act"]
    click.echo(f"Adjustments needed: {len(act['adjustments'])}")
    click.echo(f"Recommendations: {len(act['recommendations'])}")
    
    if verbose and act['adjustments']:
        click.echo("\nRequired Adjustments:")
        for adj in act['adjustments']:
            click.echo(f"  - {adj['file']}: {adj['action']}")
    
    # Print any errors if they occurred
    if "error" in results:
        click.echo("\nErrors:")
        click.echo(f"Error: {results['error']}")
        click.echo(f"Phase: {results.get('phase', 'Unknown')}")
        click.echo("\nPhase Statuses:")
        for phase, status in results["phases"].items():
            click.echo(f"{phase}: {status}")

def main() -> None:
    """Main entry point for the CLI."""
    cli()

if __name__ == "__main__":
    main() 