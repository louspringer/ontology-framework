#!/usr/bin/env python3
"""Command line interface for MCP prompt."""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import pprint

from ..modules.mcp_prompt import PromptContext, MCPPrompt, PromptError

def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    config = {
        'level': level,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'force': True
    }
    if log_file:
        config['filename'] = log_file
    logging.basicConfig(**config)

def merge_config_with_args(config: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    """Merge configuration with command line arguments."""
    # Override config values with command line arguments if provided
    if args.ontology:
        config['ontologyPath'] = str(args.ontology)
    if args.targets:
        config['targetFiles'] = [str(t) for t in args.targets]
    if args.validation_rules:
        try:
            with open(args.validation_rules) as f:
                config['validationRules'] = json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load validation rules: {e}")
    if args.server:
        if 'mcpServers' not in config:
            config['mcpServers'] = {}
        config['mcpServers']['default'] = {
            'url': args.server,
            'type': args.server_type,
            'timeout': args.timeout
        }
    if args.validate is not None:
        if 'validation' not in config:
            config['validation'] = {}
        config['validation']['enabled'] = args.validate
        config['validation']['strict'] = args.strict
    return config

def add_mcp_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Add MCP subcommand to parser."""
    parser = subparsers.add_parser(
        'mcp',
        help='Execute MCP prompt pattern'
    )
    # Configuration
    parser.add_argument(
        '-c', '--config',
        type=Path,
        default=Path('.cursor/mcp.json'),
        help='Path to MCP configuration file'
    )
    
    # Ontology and targets
    parser.add_argument(
        '-o', '--ontology',
        type=Path,
        help='Path to ontology file (overrides config)'
    )
    parser.add_argument(
        '-t', '--targets',
        type=Path,
        nargs='+',
        help='Target files to process (overrides config)'
    )
    
    # Validation
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Enable validation'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict validation'
    )
    parser.add_argument(
        '-r', '--validation-rules',
        type=Path,
        help='Path to validation rules JSON file'
    )
    
    # Server configuration
    parser.add_argument(
        '-s', '--server',
        help='SPARQL endpoint URL'
    )
    parser.add_argument(
        '--server-type',
        choices=['sparql', 'graphdb', 'stardog'],
        default='sparql',
        help='Server type'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Server timeout in seconds'
    )
    
    # Output control
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--log-file',
        help='Log file path'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format'
    )
    
    parser.set_defaults(func=run_mcp)

def run_mcp(args: argparse.Namespace) -> int:
    """Run MCP prompt with given arguments."""
    setup_logging(args.verbose, args.log_file)
    logger = logging.getLogger(__name__)
    pp = pprint.PrettyPrinter(indent=2)
    
    try:
        # Load base configuration
        config = {}
        if args.config.exists():
            logger.info(f"Loading configuration from {args.config}")
            with open(args.config) as f:
                config = json.load(f)
        
        # Merge with command line arguments
        config = merge_config_with_args(config, args)
        
        # Create context and execute prompt
        logger.info("Initializing MCP prompt")
        context = PromptContext.from_dict(config)
        prompt = MCPPrompt(context)
        
        logger.info("Executing MCP prompt phases")
        results = prompt.execute()
        
        # Output results based on format
        if args.format == 'json':
            print(json.dumps(results, indent=2))
        else:
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