#!/usr/bin/env python3
"""
Semantic Diff Module

This module provides functions for analyzing semantic differences between Git commits
for specific Python artifacts, focusing on detecting syntax corruption and analyzing
functional changes.

Generated following ontology framework rules and ClaudeReflector constraints
Ontology-Version: 1.0.0
Behavioral-Profile: ClaudeReflector
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from semantic_diff_analyzer import SemanticDiffAnalyzer
from fuzzy_semantic_analyzer import analyze_semantic_differences

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("semantic-diff-module")

def analyze_artifact_differences(commit1: str, commit2: str, artifact_path: str) -> Dict[str, Any]:
    """
    Analyze semantic differences between two commits for a specific Python artifact
    using the basic method (compare_artifacts).
    
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
    using the semantic method (analyze_semantic_differences).
    
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

def analyze_artifact(commit1: str, commit2: str, artifact_path: str, method: str = "semantic") -> Dict[str, Any]:
    """
    Analyze differences between two commits for a specific Python artifact.
    
    Args:
        commit1: First commit hash to compare (e.g., "HEAD")
        commit2: Second commit hash to compare (e.g., a specific commit hash)
        artifact_path: Path to the specific Python artifact to analyze
        method: Analysis method to use: "basic" (compare_artifacts) or "semantic" (analyze_semantic_differences)
        
    Returns:
        Dictionary containing analysis results
    """
    if method == "basic":
        return analyze_artifact_differences(commit1, commit2, artifact_path)
    else:
        return analyze_semantic_differences_for_artifact(commit1, commit2, artifact_path)

def analyze_multiple_artifacts(commit1: str, commit2: str, artifact_paths: List[str], method: str = "semantic") -> Dict[str, Any]:
    """
    Analyze differences between two commits for multiple Python artifacts.
    
    Args:
        commit1: First commit hash to compare (e.g., "HEAD")
        commit2: Second commit hash to compare (e.g., a specific commit hash)
        artifact_paths: List of paths to the Python artifacts to analyze
        method: Analysis method to use: "basic" (compare_artifacts) or "semantic" (analyze_semantic_differences)
        
    Returns:
        Dictionary containing analysis results for all artifacts
    """
    results = {
        "commit1": commit1,
        "commit2": commit2,
        "method": method,
        "artifacts": {}
    }
    
    for artifact_path in artifact_paths:
        results["artifacts"][artifact_path] = analyze_artifact(commit1, commit2, artifact_path, method)
    
    return results

def analyze_with_llm(analysis_results: Dict[str, Any], llm_function: Callable[[Dict[str, Any]], str]) -> Dict[str, Any]:
    """
    Enhance analysis results with LLM-generated insights.
    
    Args:
        analysis_results: Results from analyze_artifact or analyze_multiple_artifacts
        llm_function: Function that takes analysis results and returns LLM-generated insights
        
    Returns:
        Dictionary containing analysis results enhanced with LLM insights
    """
    # Clone the original results to avoid modifying them
    enhanced_results = json.loads(json.dumps(analysis_results))
    
    # Add LLM insights
    if isinstance(enhanced_results, dict):
        enhanced_results["llm_insights"] = llm_function(analysis_results)
    
    return enhanced_results

# Example LLM function using a hypothetical API
def example_llm_function(analysis_results: Dict[str, Any]) -> str:
    """
    Example function to generate insights from analysis results using an LLM.
    
    In a real implementation, this would call an LLM API or use a local model.
    
    Args:
        analysis_results: Results from analyze_artifact or analyze_multiple_artifacts
        
    Returns:
        String containing LLM-generated insights
    """
    # This is a placeholder. In a real implementation, you would:
    # 1. Format the analysis results into a prompt for the LLM
    # 2. Call the LLM API or local model
    # 3. Process and return the response
    
    # Example implementation using a hypothetical API:
    # ```
    # import openai
    # 
    # # Format the prompt
    # prompt = f"Analyze the following semantic differences between Git commits:\n{json.dumps(analysis_results, indent=2)}\n\nProvide insights on the nature of these changes, potential issues, and recommendations:"
    # 
    # # Call the API
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[
    #         {"role": "system", "content": "You are an expert code reviewer specializing in semantic analysis of code changes."},
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    # 
    # # Return the insights
    # return response.choices[0].message.content
    # ```
    
    # For now, return a placeholder message
    return "LLM insights would be generated here based on the analysis results."

# Example usage with BFG9K MCP integration
def analyze_with_bfg9k_mcp(commit1: str, commit2: str, artifact_path: str) -> Dict[str, Any]:
    """
    Analyze differences between two commits for a specific Python artifact using BFG9K MCP.
    
    This function demonstrates how to integrate with the BFG9K MCP server for enhanced analysis.
    
    Args:
        commit1: First commit hash to compare (e.g., "HEAD")
        commit2: Second commit hash to compare (e.g., a specific commit hash)
        artifact_path: Path to the specific Python artifact to analyze
        
    Returns:
        Dictionary containing analysis results enhanced with BFG9K insights
    """
    # First, perform standard analysis
    results = analyze_artifact(commit1, commit2, artifact_path)
    
    # Then, enhance with BFG9K MCP
    try:
        # This is a placeholder. In a real implementation, you would:
        # 1. Connect to the BFG9K MCP server
        # 2. Send the analysis results for further processing
        # 3. Receive and incorporate the enhanced insights
        
        # Example implementation using a hypothetical API:
        # ```
        # import requests
        # 
        # # Send the analysis results to BFG9K MCP
        # response = requests.post(
        #     "http://localhost:8000/bfg9k/analyze",
        #     json=results
        # )
        # 
        # # Incorporate the BFG9K insights
        # if response.status_code == 200:
        #     bfg9k_insights = response.json()
        #     results["bfg9k_insights"] = bfg9k_insights
        # ```
        
        # For now, add a placeholder
        results["bfg9k_insights"] = "BFG9K MCP insights would be generated here."
    except Exception as e:
        logger.error(f"Failed to enhance analysis with BFG9K MCP: {e}")
    
    return results

# Example usage
if __name__ == "__main__":
    # Example 1: Basic usage
    results = analyze_artifact("HEAD", "HEAD~1", "example.py")
    print(json.dumps(results, indent=2))
    
    # Example 2: Using the basic method
    results = analyze_artifact("HEAD", "HEAD~1", "example.py", method="basic")
    print(json.dumps(results, indent=2))
    
    # Example 3: Analyzing multiple artifacts
    results = analyze_multiple_artifacts("HEAD", "HEAD~1", ["example1.py", "example2.py"])
    print(json.dumps(results, indent=2))
    
    # Example 4: Using with an LLM
    results = analyze_artifact("HEAD", "HEAD~1", "example.py")
    enhanced_results = analyze_with_llm(results, example_llm_function)
    print(json.dumps(enhanced_results, indent=2))
    
    # Example 5: Using with BFG9K MCP
    results = analyze_with_bfg9k_mcp("HEAD", "HEAD~1", "example.py")
    print(json.dumps(results, indent=2))
