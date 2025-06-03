#!/usr/bin/env python3
"""
Compare Commits Tool

This script provides functionality to compare semantic differences between Git commits
for specific Python artifacts, focusing on detecting syntax corruption and analyzing
functional changes.

Generated following ontology framework rules and ClaudeReflector constraints
Ontology-Version: 1.0.0
Behavioral-Profile: ClaudeReflector
"""

import os
import sys
import logging
import argparse
from typing import Dict, List, Any, Optional, Tuple
from semantic_diff_analyzer import SemanticDiffAnalyzer
from fuzzy_semantic_analyzer import analyze_semantic_differences

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("compare-commits")

def analyze_artifact_differences(commit1: str, commit2: str, artifact_path: str) -> Dict[str, Any]:
    """
    Analyze semantic differences between two commits for a specific Python artifact.
    
    Args:
        commit1: First commit hash to compare (e.g., "HEAD")
        commit2: Second commit hash to compare (e.g., a specific commit hash)
        artifact_path: Path to the specific Python artifact to analyze
        
    Returns:
        Dictionary containing analysis results
    """
    logger.info(f"Analyzing differences for {artifact_path} between {commit1} and {commit2}")
    
    # Initialize the semantic diff analyzer
    analyzer = SemanticDiffAnalyzer()
    
    # Analyze the specific file at both commits
    artifact1 = analyzer.analyze_file(artifact_path, commit1)
    artifact2 = analyzer.analyze_file(artifact_path, commit2)
    
    if not artifact1 or not artifact2:
        logger.error(f"Failed to analyze {artifact_path} at one or both commits")
        return {
            "error": f"Failed to analyze {artifact_path} at one or both commits",
            "commit1": commit1,
            "commit2": commit2,
            "artifact_path": artifact_path
        }
    
    # Compare the artifacts
    diff = analyzer.compare_artifacts(artifact1, artifact2)
    
    # Add the artifacts to the RDF model
    file1_uri = artifact1.to_rdf(analyzer.graph)
    file2_uri = artifact2.to_rdf(analyzer.graph)
    
    # Add the diff to the RDF model
    analyzer.add_diff_to_model(artifact1, artifact2, diff, commit1, commit2)
    
    # Save the model to a file
    output_path = f"semantic_diff_{os.path.basename(artifact_path)}_{commit1}_{commit2}.ttl"
    analyzer.save_model(output_path)
    
    # Enhance the diff with additional information
    diff["commit1"] = commit1
    diff["commit2"] = commit2
    diff["artifact_path"] = artifact_path
    diff["model_path"] = output_path
    
    return diff

def extract_triples_from_artifact(artifact_path: str, commit: str) -> List[Tuple[str, str, str]]:
    """
    Extract RDF triples from a Python artifact at a specific commit.
    
    Args:
        artifact_path: Path to the Python artifact
        commit: Commit hash
        
    Returns:
        List of triples (subject, predicate, object)
    """
    # Initialize the semantic diff analyzer
    analyzer = SemanticDiffAnalyzer()
    
    # Analyze the file
    artifact = analyzer.analyze_file(artifact_path, commit)
    
    if not artifact:
        logger.error(f"Failed to analyze {artifact_path} at commit {commit}")
        return []
    
    # Convert the artifact to RDF
    artifact.to_rdf(analyzer.graph)
    
    # Extract triples from the graph
    triples = []
    for s, p, o in analyzer.graph:
        # Convert URIRefs and Literals to strings for easier comparison
        subject = str(s)
        predicate = str(p)
        obj = str(o)
        
        # Only include triples related to this artifact
        if artifact_path in subject:
            triples.append((subject, predicate, obj))
    
    return triples

def analyze_semantic_differences_for_artifact(commit1: str, commit2: str, artifact_path: str) -> Dict[str, Any]:
    """
    Analyze semantic differences between two commits for a specific Python artifact
    using the analyze_semantic_differences function.
    
    Args:
        commit1: First commit hash to compare (e.g., "HEAD")
        commit2: Second commit hash to compare (e.g., a specific commit hash)
        artifact_path: Path to the specific Python artifact to analyze
        
    Returns:
        Dictionary containing analysis results
    """
    logger.info(f"Analyzing semantic differences for {artifact_path} between {commit1} and {commit2}")
    
    # Extract triples from both commits
    triples1 = extract_triples_from_artifact(artifact_path, commit1)
    triples2 = extract_triples_from_artifact(artifact_path, commit2)
    
    if not triples1 or not triples2:
        logger.error(f"Failed to extract triples from {artifact_path} at one or both commits")
        return {
            "error": f"Failed to extract triples from {artifact_path} at one or both commits",
            "commit1": commit1,
            "commit2": commit2,
            "artifact_path": artifact_path
        }
    
    # Analyze the differences
    diff = analyze_semantic_differences(triples1, triples2)
    
    # Enhance the diff with additional information
    diff["commit1"] = commit1
    diff["commit2"] = commit2
    diff["artifact_path"] = artifact_path
    diff["triple_count1"] = len(triples1)
    diff["triple_count2"] = len(triples2)
    
    return diff

def main():
    """Main function to run the commit comparison tool."""
    parser = argparse.ArgumentParser(description="Compare semantic differences between Git commits for specific Python artifacts")
    parser.add_argument("commit1", help="First commit hash to compare (e.g., HEAD)")
    parser.add_argument("commit2", help="Second commit hash to compare")
    parser.add_argument("artifact_path", help="Path to the specific Python artifact to analyze")
    parser.add_argument("--method", choices=["basic", "semantic"], default="semantic",
                      help="Analysis method to use: basic (compare_artifacts) or semantic (analyze_semantic_differences)")
    
    args = parser.parse_args()
    
    if args.method == "basic":
        results = analyze_artifact_differences(args.commit1, args.commit2, args.artifact_path)
    else:
        results = analyze_semantic_differences_for_artifact(args.commit1, args.commit2, args.artifact_path)
    
    # Print the results
    print("\n" + "="*80)
    print(f"SEMANTIC DIFF ANALYSIS FOR {args.artifact_path}")
    print("="*80)
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return 1
    
    if args.method == "basic":
        # Print basic analysis results
        print(f"Comparing {args.artifact_path} between {args.commit1} and {args.commit2}")
        print(f"\nAdded functions: {', '.join(results['added_functions']) if results['added_functions'] else 'None'}")
        print(f"Removed functions: {', '.join(results['removed_functions']) if results['removed_functions'] else 'None'}")
        print(f"Modified functions: {', '.join(results['modified_functions']) if results['modified_functions'] else 'None'}")
        print(f"\nAdded classes: {', '.join(results['added_classes']) if results['added_classes'] else 'None'}")
        print(f"Removed classes: {', '.join(results['removed_classes']) if results['removed_classes'] else 'None'}")
        print(f"Modified classes: {', '.join(results['modified_classes']) if results['modified_classes'] else 'None'}")
        
        print(f"\nSyntax errors fixed: {len(results['syntax_errors_fixed'])}")
        print(f"Syntax errors introduced: {len(results['syntax_errors_introduced'])}")
        print(f"Comma corruptions fixed: {len(results['comma_corruptions_fixed'])}")
        print(f"Comma corruptions introduced: {len(results['comma_corruptions_introduced'])}")
        
        print(f"\nFunctional loss detected: {'Yes' if results['functional_loss'] else 'No'}")
        print(f"Corruption detected: {'Yes' if results['corruption_detected'] else 'No'}")
        
        print(f"\nSemantic model saved to: {results['model_path']}")
    else:
        # Print semantic analysis results
        print(f"Comparing {args.artifact_path} between {args.commit1} and {args.commit2}")
        print(f"Triple count in {args.commit1}: {results['triple_count1']}")
        print(f"Triple count in {args.commit2}: {results['triple_count2']}")
        print(f"Similarity score: {results['similarity_score']:.2f}")
        
        print(f"\nUnchanged triples: {len(results['unchanged'])}")
        print(f"Modified triples: {len(results['modified'])}")
        print(f"Added triples: {len(results['added'])}")
        print(f"Removed triples: {len(results['removed'])}")
        
        if results['modified']:
            print("\nModified triples (sample):")
            for i, mod in enumerate(results['modified'][:5]):  # Show up to 5 examples
                print(f"  Original: {mod['original']}")
                print(f"  Modified: {mod['modified']}")
                print(f"  Changes: {', '.join(mod['changes'])}")
                if i < len(results['modified'][:5]) - 1:
                    print()
    
    print("="*80)
    return 0

if __name__ == "__main__":
    sys.exit(main())
