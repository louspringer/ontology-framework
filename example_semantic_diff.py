#!/usr/bin/env python3
"""
Example Semantic Diff Script

This script demonstrates how to use the semantic_diff_module to analyze
semantic differences between Git commits for specific Python artifacts.

Generated following ontology framework rules and ClaudeReflector constraints
Ontology-Version: 1.0.0
Behavioral-Profile: ClaudeReflector
"""

import os
import sys
import json
import logging
import argparse
from typing import List, Dict, Any
from semantic_diff_module import (
    analyze_artifact,
    analyze_multiple_artifacts,
    analyze_with_llm,
    example_llm_function,
    analyze_with_bfg9k_mcp
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("example-semantic-diff")

def format_results(results: Dict[str, Any]) -> str:
    """
    Format analysis results for display.
    
    Args:
        results: Analysis results from semantic_diff_module
        
    Returns:
        Formatted string for display
    """
    output = []
    
    # Add header
    output.append("=" * 80)
    if "artifact_path" in results:
        output.append(f"SEMANTIC DIFF ANALYSIS FOR {results['artifact_path']}")
    else:
        output.append("SEMANTIC DIFF ANALYSIS")
    output.append("=" * 80)
    
    # Add commit information
    if "commit1" in results and "commit2" in results:
        output.append(f"Comparing between {results['commit1']} and {results['commit2']}")
    
    # Add triple counts
    if "triple_count1" in results and "triple_count2" in results:
        output.append(f"Triple count in {results['commit1']}: {results['triple_count1']}")
        output.append(f"Triple count in {results['commit2']}: {results['triple_count2']}")
    
    # Add similarity score
    if "similarity_score" in results:
        output.append(f"Similarity score: {results['similarity_score']:.2f}")
    
    # Add triple statistics
    if "unchanged_triples" in results:
        output.append(f"\nUnchanged triples: {len(results['unchanged_triples'])}")
    if "modified_triples" in results:
        output.append(f"Modified triples: {len(results['modified_triples'])}")
    if "added_triples" in results:
        output.append(f"Added triples: {len(results['added_triples'])}")
    if "removed_triples" in results:
        output.append(f"Removed triples: {len(results['removed_triples'])}")
    
    # Add modified triples sample
    if "modified_triples" in results and results["modified_triples"]:
        output.append("\nModified triples (sample):")
        for i, (original, modified, changes) in enumerate(results["modified_triples"][:3]):
            output.append(f"  Original: {original}")
            output.append(f"  Modified: {modified}")
            output.append(f"  Changes: {', '.join(changes)}")
            if i < len(results["modified_triples"][:3]) - 1:
                output.append("")
    
    # Add LLM insights if available
    if "llm_insights" in results:
        output.append("\nLLM INSIGHTS:")
        output.append("-" * 80)
        output.append(results["llm_insights"])
        output.append("-" * 80)
    
    # Add BFG9K insights if available
    if "bfg9k_insights" in results:
        output.append("\nBFG9K INSIGHTS:")
        output.append("-" * 80)
        output.append(results["bfg9k_insights"])
        output.append("-" * 80)
    
    # Add footer
    output.append("=" * 80)
    
    return "\n".join(output)

def format_multiple_results(results: Dict[str, Any]) -> str:
    """
    Format analysis results for multiple artifacts.
    
    Args:
        results: Analysis results from analyze_multiple_artifacts
        
    Returns:
        Formatted string for display
    """
    output = []
    
    # Add header
    output.append("=" * 80)
    output.append("SEMANTIC DIFF ANALYSIS FOR MULTIPLE ARTIFACTS")
    output.append("=" * 80)
    
    # Add commit information
    output.append(f"Comparing between {results['commit1']} and {results['commit2']}")
    output.append(f"Analysis method: {results['method']}")
    output.append(f"Artifacts analyzed: {len(results['artifacts'])}")
    
    # Add results for each artifact
    for artifact_path, artifact_results in results["artifacts"].items():
        output.append("\n" + "-" * 80)
        output.append(f"ARTIFACT: {artifact_path}")
        output.append("-" * 80)
        
        # Add triple counts
        if "triple_count1" in artifact_results and "triple_count2" in artifact_results:
            output.append(f"Triple count in {results['commit1']}: {artifact_results['triple_count1']}")
            output.append(f"Triple count in {results['commit2']}: {artifact_results['triple_count2']}")
        
        # Add similarity score
        if "similarity_score" in artifact_results:
            output.append(f"Similarity score: {artifact_results['similarity_score']:.2f}")
        
        # Add triple statistics
        if "unchanged_triples" in artifact_results:
            output.append(f"\nUnchanged triples: {len(artifact_results['unchanged_triples'])}")
        if "modified_triples" in artifact_results:
            output.append(f"Modified triples: {len(artifact_results['modified_triples'])}")
        if "added_triples" in artifact_results:
            output.append(f"Added triples: {len(artifact_results['added_triples'])}")
        if "removed_triples" in artifact_results:
            output.append(f"Removed triples: {len(artifact_results['removed_triples'])}")
    
    # Add footer
    output.append("\n" + "=" * 80)
    
    return "\n".join(output)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Analyze semantic differences between Git commits")
    parser.add_argument("commit1", help="First commit hash to compare (e.g., 'HEAD')")
    parser.add_argument("commit2", help="Second commit hash to compare (e.g., a specific commit hash)")
    parser.add_argument("artifacts", nargs="+", help="Paths to the Python artifacts to analyze")
    parser.add_argument("--method", choices=["basic", "semantic"], default="semantic",
                        help="Analysis method to use (default: semantic)")
    parser.add_argument("--llm", action="store_true", help="Enhance analysis with LLM insights")
    parser.add_argument("--bfg9k", action="store_true", help="Enhance analysis with BFG9K MCP")
    parser.add_argument("--output", help="Path to save the analysis results as JSON")
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Analyze artifacts
    if len(args.artifacts) == 1:
        # Single artifact
        if args.bfg9k:
            results = analyze_with_bfg9k_mcp(args.commit1, args.commit2, args.artifacts[0])
        elif args.llm:
            results = analyze_artifact(args.commit1, args.commit2, args.artifacts[0], args.method)
            results = analyze_with_llm(results, example_llm_function)
        else:
            results = analyze_artifact(args.commit1, args.commit2, args.artifacts[0], args.method)
        
        # Format and print results
        print(format_results(results))
    else:
        # Multiple artifacts
        results = analyze_multiple_artifacts(args.commit1, args.commit2, args.artifacts, args.method)
        
        # Format and print results
        print(format_multiple_results(results))
    
    # Save results to file if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Analysis results saved to {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
