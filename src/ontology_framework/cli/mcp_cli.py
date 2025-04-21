#!/usr/bin/env python3
"""Command line interface for MCP prompt."""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional
import pprint

from ..modules.mcp_prompt import PromptContext, MCPPrompt, PromptError

def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )

def add_mcp_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Add MCP subcommand to parser."""
    parser = subparsers.add_parser(
        'mcp',
        help='Execute MCP prompt pattern'
    )
    parser.add_argument(
        '-c', '--config',
        type=Path,
        default=Path('.cursor/mcp.json'),
        help='Path to MCP configuration file'
    )
    parser.add_argument(
        '-s', '--server',
        default='datapilot',
        help='MCP server to use'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Enable strict validation'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.set_defaults(func=run_mcp)

def run_mcp(args: argparse.Namespace) -> int:
    """Run MCP prompt with given arguments."""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    pp = pprint.PrettyPrinter(indent=2)
    
    try:
        # Load context from configuration
        logger.info(f"Loading configuration from {args.config}")
        context = PromptContext.from_config(args.config)
        
        # Create and execute prompt
        logger.info("Initializing MCP prompt")
        prompt = MCPPrompt(context)
        
        logger.info("Executing MCP prompt phases")
        results = prompt.execute()
        
        # Log detailed results for each phase
        for phase_name, phase_results in results.items():
            logger.info(f"\n=== {phase_name} Phase Results ===")
            if phase_name == "Discovery":
                ontology_analysis = phase_results.get("ontology_analysis", {})
                logger.info("\nOntology Analysis:")
                logger.info(f"- Classes: {len(ontology_analysis.get('classes', []))} found")
                logger.info(f"- Properties: {len(ontology_analysis.get('properties', []))} found")
                logger.info(f"- Data Properties: {len(ontology_analysis.get('data_properties', []))} found")
                logger.info(f"- Individuals: {len(ontology_analysis.get('individuals', []))} found")
                logger.info("\nClass Hierarchy:")
                for cls, subclasses in ontology_analysis.get("class_hierarchy", {}).items():
                    logger.info(f"- {cls}: {len(subclasses)} subclasses")
                logger.info("\nSHACL Shapes:")
                for shape, constraints in ontology_analysis.get("shapes", {}).items():
                    logger.info(f"- {shape}: {len(constraints)} constraints")
                
                logger.info("\nFile Analysis:")
                for file_info in phase_results.get("file_analysis", []):
                    logger.info(f"- {file_info['file']}: {file_info['size']} bytes")
            
            if args.verbose:
                logger.debug(f"\nDetailed {phase_name} Results:")
                logger.debug(pp.pformat(phase_results))
        
        logger.info("\nMCP prompt execution completed successfully")
        return 0
        
    except PromptError as e:
        logger.error(f"MCP prompt error in {e.phase} phase: {str(e)}")
        if args.verbose and e.context:
            logger.debug(f"Error context: {e.context}")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if args.verbose:
            logger.exception("Detailed error information:")
        return 2

def main() -> None:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(description='Ontology Framework CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    add_mcp_subparser(subparsers)
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        exit(1)
    
    exit(args.func(args))

if __name__ == "__main__":
    main() 