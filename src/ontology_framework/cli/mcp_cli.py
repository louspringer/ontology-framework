#!/usr/bin/env python3
"""CLI module for the MCP prompt pattern."""

import argparse
from pathlib import Path
from typing import List, Optional

from ..modules.mcp_prompt import PromptContext, MCPPrompt

def add_mcp_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Add MCP subcommand to the CLI."""
    mcp_parser = subparsers.add_parser(
        "mcp",
        help="Model Context Protocol prompt pattern",
        description="Run the MCP prompt pattern to analyze and process ontologies"
    )
    
    mcp_parser.add_argument(
        "--ontology",
        "-o",
        type=Path,
        required=True,
        help="Path to the ontology file"
    )
    
    mcp_parser.add_argument(
        "--targets",
        "-t",
        type=Path,
        nargs="+",
        required=True,
        help="Target files to analyze"
    )
    
    mcp_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    mcp_parser.set_defaults(func=run_mcp)

def run_mcp(args: argparse.Namespace) -> None:
    """Run the MCP prompt pattern."""
    # Set up the context
    context = PromptContext(
        ontology_path=args.ontology,
        target_files=args.targets
    )
    
    # Create and execute the MCP prompt
    prompt = MCPPrompt(context)
    results = prompt.execute()
    
    # Print the results
    print("\n=== MCP Prompt Results ===")
    
    # Discovery Phase Results
    print("\nDiscovery Phase:")
    discovery = results["discovery"]
    print(f"Classes found: {len(discovery['ontology_analysis']['classes'])}")
    print(f"Properties found: {len(discovery['ontology_analysis']['properties'])}")
    print(f"Data properties found: {len(discovery['ontology_analysis']['data_properties'])}")
    print(f"Individuals found: {len(discovery['ontology_analysis']['individuals'])}")
    print(f"SHACL shapes found: {len(discovery['ontology_analysis']['shapes'])}")
    
    if args.verbose:
        print("\nDetailed Class Information:")
        for cls in discovery['ontology_analysis']['classes']:
            print(f"  - {cls}")
        print("\nDetailed Property Information:")
        for prop in discovery['ontology_analysis']['properties']:
            print(f"  - {prop}")
    
    # File Analysis
    print("\nFile Analysis:")
    for file_info in discovery["file_analysis"]:
        print(f"\nFile: {file_info['file']}")
        print(f"Exists: {file_info['exists']}")
        if file_info["exists"]:
            print(f"Size: {file_info['size']} bytes")
            print(f"Last Modified: {file_info['modified']}")
    
    # Plan Phase Results
    print("\nPlan Phase:")
    plan = results["plan"]
    print(f"Classes to process: {len(plan['classes'])}")
    print(f"Properties to process: {len(plan['properties'])}")
    
    if args.verbose:
        print("\nClasses to Process:")
        for cls in plan['classes']:
            print(f"  - {cls}")
        print("\nProperties to Process:")
        for prop in plan['properties']:
            print(f"  - {prop}")
    
    # Do Phase Results
    print("\nDo Phase:")
    do = results["do"]
    print(f"Generated files: {len(do['generated_files'])}")
    print(f"Modified files: {len(do['modified_files'])}")
    
    if args.verbose and do['modified_files']:
        print("\nModified Files:")
        for file in do['modified_files']:
            print(f"  - {file}")
    
    # Check Phase Results
    print("\nCheck Phase:")
    check = results["check"]
    print(f"Validation results: {len(check['validation_results'])}")
    print(f"Test results: {len(check['test_results'])}")
    
    if args.verbose and check['validation_results']:
        print("\nValidation Results:")
        for result in check['validation_results']:
            print(f"  - {result['file']}: {result['status']}")
    
    # Act Phase Results
    print("\nAct Phase:")
    act = results["act"]
    print(f"Adjustments needed: {len(act['adjustments'])}")
    print(f"Recommendations: {len(act['recommendations'])}")
    
    if args.verbose and act['adjustments']:
        print("\nRequired Adjustments:")
        for adj in act['adjustments']:
            print(f"  - {adj['file']}: {adj['action']}")
    
    # Print any errors if they occurred
    if "error" in results:
        print("\nErrors:")
        print(f"Error: {results['error']}")
        print(f"Phase: {results.get('phase', 'Unknown')}")
        print("\nPhase Statuses:")
        for phase, status in results["phases"].items():
            print(f"{phase}: {status}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP prompt pattern CLI")
    add_mcp_subparser(parser.add_subparsers())
    args = parser.parse_args()
    args.func(args) 